import axios from "axios";
import {
  CylinderVolumeRequestPayload,
  CylinderVolumeResponse,
  CylinderVolumeConflictResponse,
} from "../models/volume";
import { PolygonVolumeRequestPayload } from "../models/polygon";

export class USSService {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async submitFlightPlan(
    payload: CylinderVolumeRequestPayload | PolygonVolumeRequestPayload,
  ): Promise<CylinderVolumeResponse> {
    try {
      const response = await axios.put(
        `${this.baseUrl}/uss/v1/flight_plan/`,
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

      return response.data as CylinderVolumeResponse;
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
