export type Service = {
  // id: string;
  name: string;
  description: string;
  category: string;
};

export type Citizen = {
  id: string;
  name: string;
  status: string;
  number: string;
  userId?: string;
  createdAt?: Date;
  updatedAt?: Date;
};
