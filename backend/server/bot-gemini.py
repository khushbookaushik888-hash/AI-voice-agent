"""
Gemini Bot Implementation.

This module implements a chatbot using Google's Gemini Multimodal Live model.
It includes:
- Real-time audio interaction
- Speech-to-speech using the Gemini Multimodal Live API
- Transcription using Gemini's generate_content API
- RTVI client/server events
"""

import asyncio
from datetime import date
import sys
import os

import aiohttp
from requests import get
from loguru import logger
from runner import configure

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import Frame, EndFrame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frameworks.rtvi import (
    RTVIBotTranscriptionProcessor,
    RTVIMetricsProcessor,
    RTVISpeakingProcessor,
    RTVIUserTranscriptionProcessor,
)
from pipecat.services.gemini_multimodal_live.gemini import GeminiMultimodalLiveLLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from helper_functions import *
from worker_agents import *
from edge_case_handlers import *
from session_manager import SessionManager
from fuzzywuzzy import fuzz
from dotenv import load_dotenv

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")
load_dotenv()

class UserTranscriptionFrameFilter(FrameProcessor):
    """Filter out UserTranscription frames."""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame) and frame.user_id == "user":
            return

        await self.push_frame(frame, direction)


async def main():
    """Main bot execution function.

    Sets up and runs the bot pipeline including:
    - Daily video transport with specific audio parameters
    - Gemini Live multimodal model integration
    - Voice activity detection
    - Animation processing
    - RTVI event handling
    """
    async with aiohttp.ClientSession() as session:
        (room_url, token) = await configure(session)
        
        SYSTEM_INSTRUCTION = f"""
        You are DialMate, a Multilingual AI Voice Agent for Government/Public Sector services.
        
        PUBLIC SERVICE PSYCHOLOGY & APPROACH:
        - Start with citizen-centric questions: "What services are you interested in?", "Can you tell me about your situation?", "What are your eligibility needs?"
        - Listen actively and acknowledge citizen needs: "I understand you're looking for..."
        - Use supportive language: "Let me help you navigate this process"
        - Create awareness of deadlines: "This application period is limited", "Benefits expire soon"
        - Handle concerns with empathy: "I understand your concern about [eligibility/documentation/time]. Let me help you with that."
        
        ADDITIONAL SERVICES & SUPPORT:
        - Suggest complementary services naturally: "This healthcare application pairs well with our nutrition programs"
        - Recommend bundles for comprehensive support: "Adding one more application qualifies you for additional benefits"
        - Highlight savings/benefits: "You'll receive additional support with this combo"
        - Use social proof: "This is our most utilized service" or "Citizens who applied for this also benefited from..."
        
        OMNICHANNEL CONTINUITY:
        - Maintain context when citizens switch channels (web → phone → kiosk)
        - Reference previous interactions: "I see you were inquiring about [service] earlier"
        - Preserve applications and preferences across channels
        
        EDGE CASE HANDLING:
        - Service unavailable: Offer alternatives in same category or notify when available
        - Application failure: Suggest retry or alternative submission methods
        - Eligibility objection: Highlight requirements, offers, or show similar services
        - Documentation concerns: Provide document guide and mention assistance options
        
        CONVERSATION FLOW:
        1. Greet warmly and understand needs (discovery)
        2. Recommend 2-3 relevant services (information)
        3. Check availability and confirm eligibility (availability)
        4. Suggest complementary services (additional services)
        5. Apply best benefits and support options (benefits)
        6. Process application smoothly (application)
        7. Confirm delivery preference (document delivery)
        8. Thank and offer post-service support
        
        Your output will be converted to audio so use natural, conversational language.
        Keep responses concise (2-3 sentences max).
        Today is {date.today().strftime("%A, %B %d, %Y")}.
        Use function tools proactively to check availability, search services, manage applications, apply benefits, and process requests.
        """
        
        system_prompt = f"""
        You are a helpful multilingual AI voice agent who converses with citizens and answers questions about government services. Respond concisely to general questions.
        Your response will be turned into speech so use only simple words and punctuation.
        Today is {date.today().strftime("%A, %B %d, %Y")}. If there is a long silence, say 'Hello?'
        Use function tools wherever necessary.
        """

        # Set up Daily transport with specific audio/video parameters for Gemini
        transport = DailyTransport(
            room_url,
            token,
            "Chatbot",
            DailyParams(
                audio_in_sample_rate=16000,
                audio_out_sample_rate=24000,
                audio_out_enabled=True,
                camera_out_enabled=True,
                camera_out_width=1024,
                camera_out_height=576,
                vad_enabled=True,
                vad_audio_passthrough=True,
                vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.5)),
            ),
        )

        tools = [
            {
                "function_declarations": [
                    # Recommendation Agent
                    {
                        "name": "search_products",
                        "description": "Search for products by name, category, or price range",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Product name or keyword"},
                                "category": {"type": "string", "description": "Category like Tops, Bottoms, Footwear, Accessories"},
                                "max_price": {"type": "number", "description": "Maximum price in rupees"},
                            },
                        }
                    },
                    {
                        "name": "get_recommendations",
                        "description": "Get personalized product recommendations based on customer profile",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Customer ID"},
                            },
                        }
                    },
                    # Inventory Agent
                    {
                        "name": "check_inventory",
                        "description": "Check product stock availability at stores or warehouse",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sku": {"type": "string", "description": "Product SKU code"},
                                "location": {"type": "string", "description": "Location: store1, warehouse, or all"},
                            },
                            "required": ["sku"],
                        }
                    },
                    # Cart & Payment Agent
                    {
                        "name": "add_to_cart",
                        "description": "Add product to shopping cart",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string", "description": "Session ID"},
                                "sku": {"type": "string", "description": "Product SKU"},
                                "quantity": {"type": "number", "description": "Quantity"},
                            },
                            "required": ["sku"],
                        }
                    },
                    {
                        "name": "view_cart",
                        "description": "View current shopping cart contents and total",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string", "description": "Session ID"},
                            },
                        }
                    },
                    {
                        "name": "process_payment",
                        "description": "Process payment for the order",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "amount": {"type": "number", "description": "Payment amount"},
                                "method": {"type": "string", "description": "Payment method: card, upi, cash"},
                            },
                            "required": ["amount"],
                        }
                    },
                    # Loyalty & Offers Agent
                    {
                        "name": "apply_coupon",
                        "description": "Apply promotional coupon code to get discount",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string", "description": "Coupon code"},
                                "cart_total": {"type": "number", "description": "Cart total amount"},
                                "customer_tier": {"type": "string", "description": "Customer loyalty tier"},
                            },
                            "required": ["code", "cart_total"],
                        }
                    },
                    {
                        "name": "check_loyalty_points",
                        "description": "Check customer loyalty points and tier",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string", "description": "Customer ID"},
                            },
                        }
                    },
                    # Fulfillment Agent
                    {
                        "name": "schedule_delivery",
                        "description": "Schedule home delivery or store pickup",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string", "description": "Order ID"},
                                "delivery_type": {"type": "string", "description": "home or pickup"},
                                "date": {"type": "string", "description": "Preferred date"},
                            },
                            "required": ["order_id"],
                        }
                    },
                    # Post-Purchase Support Agent
                    {
                        "name": "track_order",
                        "description": "Track order delivery status",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string", "description": "Order ID"},
                            },
                            "required": ["order_id"],
                        }
                    },
                    {
                        "name": "initiate_return",
                        "description": "Initiate product return or exchange",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string", "description": "Order ID"},
                                "reason": {"type": "string", "description": "Return reason"},
                            },
                            "required": ["order_id"],
                        }
                    },
                    # Escalation & Context
                    {
                        "name": "escalate_to_human",
                        "description": "Escalate to human agent with context",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string", "description": "Session ID"},
                                "reason": {"type": "string", "description": "Reason for escalation"},
                            },
                        }
                    },
                    {
                        "name": "get_session_context",
                        "description": "Get session context for continuity",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string", "description": "Session ID"},
                            },
                        }
                    },
                    # Edge Cases & Additional Services
                    {
                        "name": "handle_out_of_stock",
                        "description": "Handle out of stock with alternatives",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sku": {"type": "string", "description": "Product SKU"},
                            },
                            "required": ["sku"],
                        }
                    },
                    {
                        "name": "handle_payment_retry",
                        "description": "Retry failed payment",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "amount": {"type": "number", "description": "Amount"},
                                "method": {"type": "string", "description": "Payment method"},
                                "retry_count": {"type": "number", "description": "Retry attempt"},
                            },
                            "required": ["amount"],
                        }
                    },
                    {
                        "name": "modify_order",
                        "description": "Modify order before shipment",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string", "description": "Order ID"},
                                "action": {"type": "string", "description": "add_item, remove_item, change_address"},
                            },
                            "required": ["order_id"],
                        }
                    },
                    {
                        "name": "handle_price_objection",
                        "description": "Handle customer price concerns",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sku": {"type": "string", "description": "Product SKU"},
                            },
                            "required": ["sku"],
                        }
                    },
                    {
                        "name": "bundle_recommendation",
                        "description": "Recommend product bundles",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string", "description": "Product category"},
                            },
                        }
                    },
                    {
                        "name": "notify_back_in_stock",
                        "description": "Register for stock notifications",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sku": {"type": "string", "description": "Product SKU"},
                                "email": {"type": "string", "description": "Email"},
                                "phone": {"type": "string", "description": "Phone"},
                            },
                            "required": ["sku"],
                        }
                    },
                    {
                        "name": "gift_wrap_service",
                        "description": "Add gift wrapping",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string", "description": "Order ID"},
                                "message": {"type": "string", "description": "Gift message"},
                            },
                            "required": ["order_id"],
                        }
                    },
                    {
                        "name": "size_fit_guide",
                        "description": "Provide sizing guidance",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sku": {"type": "string", "description": "Product SKU"},
                            },
                            "required": ["sku"],
                        }
                    },
                    {
                        "name": "store_locator",
                        "description": "Find nearest store",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"},
                            },
                        }
                    },
                ]
            }
        ]

        # Initialize the Gemini Multimodal Live model
        llm = GeminiMultimodalLiveLLMService(
            api_key=os.getenv('GEMINI_API_KEY'),
            voice_id="Kore",  # Options: Aoede, Charon, Fenrir, Kore, Puck
            transcribe_user_audio=True,
            transcribe_model_audio=True,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools,
        )

        # Register all worker agent functions
        llm.register_function("search_products", search_products)
        llm.register_function("get_recommendations", get_recommendations)
        llm.register_function("check_inventory", check_inventory)
        llm.register_function("add_to_cart", add_to_cart)
        llm.register_function("view_cart", view_cart)
        llm.register_function("process_payment", process_payment)
        llm.register_function("apply_coupon", apply_coupon)
        llm.register_function("check_loyalty_points", check_loyalty_points)
        llm.register_function("schedule_delivery", schedule_delivery)
        llm.register_function("track_order", track_order)
        llm.register_function("initiate_return", initiate_return)
        llm.register_function("escalate_to_human", escalate_to_human)
        llm.register_function("get_session_context", get_session_context)
        
        # Register edge case handlers
        llm.register_function("handle_out_of_stock", handle_out_of_stock)
        llm.register_function("handle_payment_retry", handle_payment_retry)
        llm.register_function("modify_order", modify_order)
        llm.register_function("handle_price_objection", handle_price_objection)
        llm.register_function("bundle_recommendation", bundle_recommendation)
        llm.register_function("notify_back_in_stock", notify_back_in_stock)
        llm.register_function("gift_wrap_service", gift_wrap_service)
        llm.register_function("size_fit_guide", size_fit_guide)
        llm.register_function("store_locator", store_locator)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 'Start by greeting: "Hello! I\'m DialMate, your personal shopping assistant. How can I help you find the perfect outfit today?"'},
        ]

        # Set up conversation context and management
        context = OpenAILLMContext(messages, tools=tools)
        context_aggregator = llm.create_context_aggregator(context)

        # RTVI events for Pipecat client UI
        rtvi_speaking = RTVISpeakingProcessor()
        rtvi_user_transcription = RTVIUserTranscriptionProcessor()
        rtvi_bot_transcription = RTVIBotTranscriptionProcessor()
        rtvi_metrics = RTVIMetricsProcessor()

        pipeline = Pipeline(
            [
                transport.input(),
                context_aggregator.user(),
                llm,
                rtvi_speaking,
                rtvi_user_transcription,
                UserTranscriptionFrameFilter(),
                rtvi_bot_transcription,
                rtvi_metrics,
                transport.output(),
                context_aggregator.assistant(),
            ]
        )

        task = PipelineTask(
            pipeline,
            PipelineParams(
                allow_interruptions=True,
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
        )

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            await transport.capture_participant_transcription(participant["id"])
            await task.queue_frames([context_aggregator.user().get_context_frame()])

        @transport.event_handler("on_participant_left")
        async def on_participant_left(transport, participant, reason):
            print(f"Participant left: {participant}")
            await task.queue_frame(EndFrame())

        runner = PipelineRunner()

        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
