import Car from "./Car";
import { CarOptions } from "./CarOptions";

export interface CarPaginatedResultWithOptions {
  entities: Car[];
  total_entities: number;
  options?: CarOptions;
}
