import { NextRequest, NextResponse } from "next/server";

import { auth } from "@clerk/nextjs/server";

import { prisma } from "@/lib/db";
import { citizenObj } from "@/lib/zod";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");

    if (id) {
      const citizen = await prisma.citizen.findUnique({
        where: {
          id: id,
        },
      });

      if (!citizen) {
        return NextResponse.json(
          { msg: "Citizen not found" },
          { status: 404 }
        );
      }

      return NextResponse.json(citizen);
    }

    const isAuthenticated = await auth();
    if (!isAuthenticated.userId) {
      throw new Error("Unauthorized");
    }

    const citizensInDb = await prisma.citizen.findMany({
      where: {
        userId: isAuthenticated.userId,
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    return NextResponse.json(citizensInDb);
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
    const data = citizenObj.safeParse(rawData);

    if (!data.success) {
      throw new Error(data.error.message);
    }

    const citizen = await prisma.citizen.create({
      data: {
        name: data.data.name,
        status: data.data.status,
        number: data.data.number.toString(),
        userId: isAuthenticated.userId,
      },
    });

    return NextResponse.json(citizen);
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

    const citizen = await prisma.citizen.delete({
      where: { id: rawData.id },
    });

    return NextResponse.json(citizen);
  } catch (err) {
    console.error(err);
    return NextResponse.json({ msg: "Something went wrong" });
  }
}
