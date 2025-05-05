export interface JobStatus {
  id: number;
  status: 'Pending' | 'Running' | 'Completed' | 'Failed' | 'Processing';
  job_name?: string;
  result_url?: string;
}
  