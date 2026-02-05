'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from 'next/link';

interface Farm {
  uuid: string;
  code: string;
  project: string;
  spv: string;
  farm_types?: {
    type_title: string;
  };
}

export default function FarmsPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user) return;

    const fetchFarms = async () => {
      setIsLoading(true);
      const { data, error } = await api.get<{ farms: Farm[] }>('/farms');
      
      if (data) {
        setFarms(data.farms);
      } else {
        setError(error || 'Failed to fetch farms');
      }
      setIsLoading(false);
    };

    fetchFarms();
  }, [user, authLoading]);

  if (authLoading) {
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
        <p className="text-muted-foreground mb-6">Please sign in to view your farms.</p>
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
          <h1 className="text-3xl font-bold tracking-tight">Farms</h1>
          <p className="text-muted-foreground">Manage your wind farm assets.</p>
        </div>
        <Button>Add Farm</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Farms</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-10">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : error ? (
            <div className="bg-destructive/10 text-destructive p-4 rounded-md">
              {error}
            </div>
          ) : (
            <Table>
              <TableCaption>A list of your managed wind farms.</TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Code</TableHead>
                  <TableHead>Project</TableHead>
                  <TableHead>SPV</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {farms.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-10 text-muted-foreground">
                      No farms found.
                    </TableCell>
                  </TableRow>
                ) : (
                  farms.map((farm) => (
                    <TableRow key={farm.uuid}>
                      <TableCell className="font-medium">{farm.code}</TableCell>
                      <TableCell>{farm.project}</TableCell>
                      <TableCell>{farm.spv}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {farm.farm_types?.type_title || 'Unknown'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/farms/${farm.uuid}`}>View</Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
