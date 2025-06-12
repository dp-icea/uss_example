import axios from "axios";
import {
  CylinderVolumeRequestPayload,
  FlightRequestResponse,
  CylinderVolumeSchema,
} from "../models/volume";
import { PolygonVolumeSchema } from "../models/polygon";
import { PolygonVolumeRequestPayload } from "../models/polygon";

export interface QueryConflictsResponse {
  status: number;
  message: string;
  data: {
    operational_intents: Array<CylinderVolumeSchema | PolygonVolumeSchema>;
    constraints: Array<CylinderVolumeSchema | PolygonVolumeSchema>;
  };
}

export class USSService {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async submitFlightPlan(
    payload: CylinderVolumeRequestPayload | PolygonVolumeRequestPayload,
  ): Promise<FlightRequestResponse> {
    try {
      const response = await axios.put(
        `${this.baseUrl}/uss/v1/flight_plan/with_conflict`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      if (response.status !== 201) {
        throw new Error(`Expected status 201, but got ${response.status}`);
      }

      return response.data as FlightRequestResponse;
    } catch (error: any) {
      // Re-throw the error with response data for proper handling
      if (error.response) {
        const customError = new Error(error.message);
        (customError as any).response = error.response;
        throw customError;
      }
      throw error;
    }
  }

  async queryConflicts(
    payload: CylinderVolumeRequestPayload | PolygonVolumeRequestPayload,
  ): Promise<QueryConflictsResponse> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/uss/v1/flight_plan/query_conflicts`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      if (response.status !== 200) {
        throw new Error(`Expected status 200, but got ${response.status}`);
      }

      return response.data as QueryConflictsResponse;
    } catch (error: any) {
      // Re-throw the error with response data for proper handling
      if (error.response) {
        const customError = new Error(error.message);
        (customError as any).response = error.response;
        throw customError;
      }
      throw error;
    }
  }
}
