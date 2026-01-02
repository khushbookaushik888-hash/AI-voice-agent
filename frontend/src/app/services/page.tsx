"use client";

import { useEffect, useState } from "react";

import { useSession } from "@clerk/nextjs";
import { Plus, Trash } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Service } from "@/lib/types";

const ServicesList = () => {
  const user = useSession();
  const userId = user.session?.id;
  const [services, setServices] = useState<Service[]>([]);
  const [error, setError] = useState<string>("");

  const addNewService = async (newService: Service) => {
    try {
      await fetch("/api/service", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newService),
      });

      fetchServices();
    } catch (err) {
      console.error(err);
      setError("Something went wrong");
    }
  };

  const deleteService = async (deletedService: Service) => {
    try {
      await fetch("/api/service", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(deletedService),
      });

      fetchServices();
    } catch (err) {
      console.error(err);
      setError("Something went wrong");
    }
  };

  const fetchServices = async () => {
    try {
      const res = await fetch("/api/service");
      const data = await res.json();
      setServices(data);
    } catch (err) {
      console.error(err);
      setError("Something went wrong");
    }
  };

  useEffect(() => {
    fetchServices();
  }, []);

  if (!user.isLoaded) {
    return (
      <div className="flex h-[50dvh] items-center justify-center">
        <div className="size-10 animate-spin rounded-full border-b-2 border-t-2 border-brand-foreground" />
      </div>
    );
  }

  return (
    <div className="mt-16 px-2">
      <div className="mb-4 flex w-full flex-row-reverse items-center justify-between px-1">
        <Dialog>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-x-2 bg-brand-foreground text-lg text-black hover:bg-brand-foreground/80">
              Add new service
              <Plus className="size-4" />
            </Button>
          </DialogTrigger>

          <DialogContent className="border-brand-foreground bg-[#232323] text-brand-foreground">
            {/* <DialogHeader> */}
            <form
              action={(formData: FormData) => {
                const name = formData.get("name") as string;
                const description = formData.get("description") as string;
                const category = formData.get("category") as string;
                addNewService({ name, description, category });
              }}
            >
              <DialogTitle className="text-2xl">Add new service</DialogTitle>
              <label id="name">
                Service Name
                <Input
                  type="text"
                  placeholder="Service name"
                  name="name"
                  id="name"
                  className="bg-[#232323]"
                />
              </label>

              <label>
                Description
                <Textarea
                  placeholder="Description"
                  id="description"
                  name="description"
                  className="bg-[#232323]"
                />
              </label>

              <label id="name">
                Category
                <Input
                  type="text"
                  placeholder="Category"
                  id="category"
                  name="category"
                  className="bg-[#232323]"
                />
              </label>

              <Button className="mt-4 w-full bg-brand-foreground text-brand-bg hover:bg-brand-foreground/80">
                Submit
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="rounded-lg bg-[#232323] py-5">
        <div className="grid grid-cols-12 items-center gap-4 px-1 text-center text-xl text-brand-foreground">
          <p className="col-span-2">No.</p>
          <p className="col-span-2">Name</p>
          <p className="col-span-5">Description</p>
          <p className="col-span-2">Category</p>
        </div>
        {services.map((service, no) => (
          <div
            key={no}
            className="mt-2 grid grid-cols-12 items-center gap-4 truncate text-center text-brand-foreground transition-all delay-100 duration-100 hover:bg-black/20"
          >
            <p className="col-span-2 px-1"> {no + 1}</p>
            <p className="col-span-2 truncate px-1">{service.name}</p>
            <p className="col-span-5 truncate px-1">{service.description}</p>
            <p className="col-span-2 px-1"> {service.category}</p>
            <div className="col-span-1 flex items-center justify-center">
              <Trash
                className="size-4 cursor-pointer"
                onClick={() => deleteService(service)}
              />
            </div>
          </div>
        ))}
      </div>

      {error && <p className="mt-4 text-center text-red-500">{error}</p>}
    </div>
  );
};

export default ServicesList;
