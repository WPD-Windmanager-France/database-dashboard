'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Link from 'next/link';
import { ArrowLeft, Wind, MapPin, Settings, Info, Zap } from 'lucide-react';

interface FarmDetail {
  farm: {
    uuid: string;
    code: string;
    spv: string;
    project: string;
    type: string;
  };
  status: {
    farm_status: string;
    tcma_status: string;
  } | null;
  location: {
    country: string;
    region: string;
    department: string;
  } | null;
  technical: {
    turbineCount: number;
    totalPowerMW: number;
    manufacturer: string | null;
    substationCount: number;
    wtgCount: number;
  };
  administration: {
    subsidiary: string | null;
  };
  recentPerformances: any[];
}

export default function FarmDetailPage({ params }: { params: { uuid: string } }) {
  const { user, isLoading: authLoading } = useAuth();
  const [data, setData] = useState<FarmDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (authLoading || !user) return;

    const fetchDetail = async () => {
      setIsLoading(true);
      const { data, error } = await api.get<FarmDetail>(`/farms/${params.uuid}/summary`);
      
      if (data) {
        setData(data);
      } else {
        setError(error || 'Failed to fetch farm details');
      }
      setIsLoading(false);
    };

    fetchDetail();
  }, [user, authLoading, params.uuid]);

  if (authLoading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container mx-auto py-10 px-4">
        <Button variant="ghost" asChild className="mb-6">
          <Link href="/farms"><ArrowLeft className="mr-2 h-4 w-4" /> Back to List</Link>
        </Button>
        <Card className="bg-destructive/10 border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error || 'Farm not found'}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { farm, status, location, technical, administration } = data;

  return (
    <div className="container mx-auto py-10 px-4">
      <Button variant="ghost" asChild className="mb-6">
        <Link href="/farms"><ArrowLeft className="mr-2 h-4 w-4" /> Back to List</Link>
      </Button>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{farm.project}</h1>
            <Badge variant="outline">{farm.code}</Badge>
            <Badge>{farm.type}</Badge>
          </div>
          <p className="text-muted-foreground mt-1">{farm.spv}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Edit Farm</Button>
          <Button variant="destructive">Delete</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.farm_status || 'N/A'}</div>
            <p className="text-xs text-muted-foreground mt-1">TCMA: {status?.tcma_status || 'N/A'}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Power</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{technical.totalPowerMW} MW</div>
            <p className="text-xs text-muted-foreground mt-1">Installed Capacity</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Turbines</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{technical.turbineCount}</div>
            <p className="text-xs text-muted-foreground mt-1">{technical.manufacturer || 'Multiple'} units</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Region</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{location?.region || 'N/A'}</div>
            <p className="text-xs text-muted-foreground mt-1">{location?.country || 'France'}</p>
          </CardContent>
        </Card>
      </div>

      <Tabs className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger active={activeTab === 'overview'} onClick={() => setActiveTab('overview')}>Overview</TabsTrigger>
          <TabsTrigger active={activeTab === 'technical'} onClick={() => setActiveTab('technical')}>Technical</TabsTrigger>
          <TabsTrigger active={activeTab === 'location'} onClick={() => setActiveTab('location')}>Location</TabsTrigger>
          <TabsTrigger active={activeTab === 'admin'} onClick={() => setActiveTab('admin')}>Administration</TabsTrigger>
        </TabsList>

        <TabsContent active={activeTab === 'overview'}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center"><Info className="mr-2 h-5 w-5" /> General Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 border-b pb-2">
                  <span className="text-sm font-medium">Project Name</span>
                  <span className="text-sm text-right">{farm.project}</span>
                </div>
                <div className="grid grid-cols-2 border-b pb-2">
                  <span className="text-sm font-medium">SPV</span>
                  <span className="text-sm text-right">{farm.spv}</span>
                </div>
                <div className="grid grid-cols-2 border-b pb-2">
                  <span className="text-sm font-medium">Internal Code</span>
                  <span className="text-sm text-right font-mono">{farm.code}</span>
                </div>
                <div className="grid grid-cols-2 border-b pb-2">
                  <span className="text-sm font-medium">Farm Type</span>
                  <span className="text-sm text-right">{farm.type}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center"><Zap className="mr-2 h-5 w-5" /> Performance Summary</CardTitle>
              </CardHeader>
              <CardContent>
                {data.recentPerformances.length > 0 ? (
                  <div className="space-y-4">
                    {data.recentPerformances.map((perf, i) => (
                      <div key={i} className="grid grid-cols-2 border-b pb-2">
                        <span className="text-sm font-medium">Year {perf.year}</span>
                        <span className="text-sm text-right">{perf.amount} MWh</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-10">No recent performance data available.</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent active={activeTab === 'technical'}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><Wind className="mr-2 h-5 w-5" /> Technical Specifications</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">Manufacturer</span>
                <span className="text-sm text-right">{technical.manufacturer || 'N/A'}</span>
              </div>
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">Number of Turbines</span>
                <span className="text-sm text-right">{technical.turbineCount}</span>
              </div>
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">WTG Registered Count</span>
                <span className="text-sm text-right">{technical.wtgCount}</span>
              </div>
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">Total Power</span>
                <span className="text-sm text-right">{technical.totalPowerMW} MW</span>
              </div>
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">Substations</span>
                <span className="text-sm text-right">{technical.substationCount}</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent active={activeTab === 'location'}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><MapPin className="mr-2 h-5 w-5" /> Geographic Location</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">Country</span>
                <span className="text-sm text-right">{location?.country || 'France'}</span>
              </div>
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">Region</span>
                <span className="text-sm text-right">{location?.region || 'N/A'}</span>
              </div>
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">Department</span>
                <span className="text-sm text-right">{location?.department || 'N/A'}</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent active={activeTab === 'admin'}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><Settings className="mr-2 h-5 w-5" /> Administration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 border-b pb-2">
                <span className="text-sm font-medium">Windmanager Subsidiary</span>
                <span className="text-sm text-right">{administration.subsidiary || 'N/A'}</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
