'use client';

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useAuth } from "@/context/AuthContext"
import Link from "next/link"

export default function Home() {
  const { user, login, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <Card className="w-[400px]">
        <CardHeader>
          <CardTitle>WNDMNGR</CardTitle>
          <CardDescription>
            WPD Windmanager France - Asset Management Platform
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {user ? (
            <>
              <div className="space-y-1">
                <p className="text-sm font-medium">Welcome, {user.name}</p>
                <p className="text-xs text-muted-foreground">{user.email}</p>
              </div>
              <p className="text-sm text-muted-foreground">
                You are successfully authenticated.
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                <Button className="flex-1" asChild>
                  <Link href="/dashboard">Go to Dashboard</Link>
                </Button>
                <Button variant="outline" className="flex-1" asChild>
                  <Link href="/farms">Farm List</Link>
                </Button>
                <Button variant="destructive" className="w-full" onClick={logout}>Sign Out</Button>
              </div>
            </>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">
                Welcome to the wind farm management platform.
              </p>
              <Button onClick={login}>Sign in with Microsoft</Button>
            </>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
