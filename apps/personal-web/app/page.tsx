import { Overview } from "../components/portal/overview";

export default function PersonalHome() {
  return (
    <Overview
      socialUrl={process.env.PUBLIC_APP_URL ?? "http://localhost:3000"}
      researcherUrl={process.env.RESEARCHER_APP_URL ?? "http://localhost:3002"}
    />
  );
}
