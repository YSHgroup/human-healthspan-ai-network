"use client";

import { useEffect, useState } from "react";
import { VerifyEmailForm } from "@/app/components/IdentityForms";

export default function VerifyEmailPage() {
  const [token, setToken] = useState("");
  useEffect(() => {
    setToken(new URLSearchParams(window.location.search).get("token") ?? "");
  }, []);
  return <VerifyEmailForm initialToken={token} />;
}
