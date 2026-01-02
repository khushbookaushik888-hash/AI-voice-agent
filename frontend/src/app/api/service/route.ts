import { NextRequest, NextResponse } from "next/server";

import { auth } from "@clerk/nextjs/server";

import { prisma } from "@/lib/db";
import { serviceObj } from "@/lib/zod";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get("userId");

    if (userId) {
      const services = await prisma.service.findMany({
        where: {
          userId: userId,
        },
      });
      return NextResponse.json(services);
    }

    const isAuthenticated = await auth();
    if (!isAuthenticated.userId) {
      throw new Error("Unauthorized");
    }

    const servicesInDb = await prisma.service.findMany({
      where: {
        userId: isAuthenticated.userId,
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    return NextResponse.json(servicesInDb);
  } catch (err) {
    console.error(err);
    return NextResponse.json({ msg: "Something went wrong" });
  }
}

export async function POST(request: NextRequest) {
  try {
    const isAuthenticated = await auth();
    if (!isAuthenticated.userId) {
      throw new Error("Unauthorized");
    }

    const rawData = await request.json();
    const data = serviceObj.safeParse(rawData);

    if (!data.success) {
      throw new Error(data.error.message);
    }

    const service = await prisma.service.create({
      data: {
        name: data.data.name,
        description: data.data.description,
        category: data.data.category,
        userId: isAuthenticated.userId,
      },
    });

    return NextResponse.json(service);
  } catch (err) {
    console.error(err);
    return NextResponse.json({ msg: "Something went wrong" });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const isAuthenticated = await auth();
    if (!isAuthenticated.userId) {
      throw new Error("Unauthorized");
    }

    const rawData = await request.json();

    const service = await prisma.service.delete({
      where: { id: rawData.id },
    });

    return NextResponse.json(service);
  } catch (err) {
    console.error(err);
    return NextResponse.json({ msg: "Something went wrong" });
  }
}
