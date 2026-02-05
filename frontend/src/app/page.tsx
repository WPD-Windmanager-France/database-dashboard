import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function Home() {
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
          <p className="text-sm text-muted-foreground">
            Welcome to the wind farm management platform.
          </p>
          <Button>Sign in with Microsoft</Button>
        </CardContent>
      </Card>
    </main>
  )
}
