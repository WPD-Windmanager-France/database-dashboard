'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from 'next/link';
import { 
  LayoutDashboard, 
  Wind, 
  Zap, 
  PlusCircle, 
  List, 
  Database,
  ArrowRight,
  Activity
} from 'lucide-react';

interface Stats {
  totalFarms: number;
  byType: Record<string, number>;
  totalTurbines: number;
  totalPowerMW: number;
}

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading || !user) return;

    const fetchStats = async () => {
      setIsLoading(true);
      const { data, error } = await api.get<Stats>('/farms/stats');
      
      if (data) {
        setStats(data);
      } else {
        setError(error || 'Failed to fetch statistics');
      }
      setIsLoading(false);
    };

    fetchStats();
  }, [user, authLoading]);

  if (authLoading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24 text-center">
        <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
        <p className="text-muted-foreground mb-6">Please sign in to view the dashboard.</p>
        <Button asChild>
          <Link href="/">Back to Home</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10 px-4">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center">
            <LayoutDashboard className="mr-2 h-8 w-8 text-primary" /> Dashboard
          </h1>
          <p className="text-muted-foreground">High-level overview of your asset portfolio.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link href="/farms"><List className="mr-2 h-4 w-4" /> View List</Link>
          </Button>
          <Button asChild>
            <Link href="/farms/new"><PlusCircle className="mr-2 h-4 w-4" /> Add Farm</Link>
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-md mb-8">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalFarms || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Managed wind and solar farms</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Global Capacity</CardTitle>
            <Zap className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalPowerMW || 0} MW</div>
            <p className="text-xs text-muted-foreground mt-1">Total installed power</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Turbines</CardTitle>
            <Wind className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.totalTurbines || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Total operational units</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card>
          <CardHeader>
            <CardTitle>Asset Distribution</CardTitle>
            <CardDescription>Breakdown of assets by energy source.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats && Object.entries(stats.byType).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between border-b pb-2">
                  <div className="flex items-center gap-2">
                    <div className={`h-3 w-3 rounded-full ${
                      type === 'Wind' ? 'bg-blue-500' : type === 'Solar' ? 'bg-orange-400' : 'bg-green-500'
                    }`} />
                    <span className="text-sm font-medium">{type}</span>
                  </div>
                  <Badge variant="secondary">{count} farms</Badge>
                </div>
              ))}
              {!stats && <p className="text-sm text-muted-foreground text-center py-4">No distribution data.</p>}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Access</CardTitle>
            <CardDescription>Useful links and documentation.</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-4">
            <Button variant="outline" className="justify-start h-auto py-4 px-4" asChild>
              <Link href="/farms">
                <div className="flex items-center gap-3 w-full">
                  <div className="bg-primary/10 p-2 rounded-lg text-primary">
                    <List className="h-5 w-5" />
                  </div>
                  <div className="text-left flex-1">
                    <div className="font-semibold text-sm">Farm Inventory</div>
                    <div className="text-xs text-muted-foreground">Manage your detailed farm records</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </Link>
            </Button>
            <Button variant="outline" className="justify-start h-auto py-4 px-4" asChild>
              <Link href="/docs">
                <div className="flex items-center gap-3 w-full">
                  <div className="bg-primary/10 p-2 rounded-lg text-primary">
                    <Database className="h-5 w-5" />
                  </div>
                  <div className="text-left flex-1">
                    <div className="font-semibold text-sm">Technical Docs</div>
                    <div className="text-xs text-muted-foreground">Explore database schema and metadata</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
