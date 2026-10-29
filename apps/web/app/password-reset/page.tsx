"use client";

import { useEffect, useState } from "react";
import { PasswordResetForm } from "@/app/components/IdentityForms";

export default function PasswordResetPage() {
  const [token, setToken] = useState("");
  useEffect(() => {
    setToken(new URLSearchParams(window.location.search).get("token") ?? "");
  }, []);
  return <PasswordResetForm initialToken={token} />;
}
