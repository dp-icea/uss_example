import axios from 'axios';
import { VolumeRequestPayload } from '../models/volume';

export class VolumeApiService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async submitFlightPlan(payload: VolumeRequestPayload): Promise<any> {
    try {
      const response = await axios.put(
        `${this.baseUrl}/uss/v1/flight_plan/`,
        payload,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
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
