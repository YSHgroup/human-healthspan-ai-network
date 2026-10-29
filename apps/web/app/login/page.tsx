"use client";

import { useEffect, useState } from "react";
import { LoginForm } from "@/app/components/IdentityForms";

export default function LoginPage() {
  const [message, setMessage] = useState<string>();
  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    if (query.get("passwordChanged") === "1") {
      setMessage("Your password was changed. Sign in with your new password.");
    } else if (query.get("verified") === "1") {
      setMessage("Your email has been verified. You can now sign in.");
    }
  }, []);
  return <LoginForm initialMessage={message} />;
}
