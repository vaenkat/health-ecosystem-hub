import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { Pill, Package, AlertTriangle, TrendingUp, Settings, LogOut } from "lucide-react";

const PharmacyDashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ totalItems: 0, lowStock: 0, urgentOrders: 0 });
  const [inventory, setInventory] = useState<any[]>([]);
  const [urgentOrders, setUrgentOrders] = useState<any[]>([]);
  const [aiApiKey, setAiApiKey] = useState("");

  useEffect(() => {
    checkUser();
    fetchData();
  }, []);

  const checkUser = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      navigate("/auth/pharmacy");
      return;
    }
    setUser(session.user);
  };

  const fetchData = async () => {
    try {
      // Fetch inventory stats
      const { data: inventoryData, count: totalItems } = await supabase
        .from("inventory")
        .select("*, medications(*)", { count: "exact" })
        .order("updated_at", { ascending: false })
        .limit(10);

      setInventory(inventoryData || []);

      const lowStock = inventoryData?.filter(
        (item) => item.quantity <= item.reorder_level
      ).length || 0;

      // Fetch urgent orders
      const { data: ordersData, count: urgentCount } = await supabase
        .from("hospital_orders")
        .select("*, medications(*)", { count: "exact" })
        .in("urgency", ["urgent", "emergency"])
        .eq("status", "pending")
        .order("created_at", { ascending: false })
        .limit(5);

      setUrgentOrders(ordersData || []);

      setStats({
        totalItems: totalItems || 0,
        lowStock,
        urgentOrders: urgentCount || 0,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    navigate("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-success-light via-background to-secondary-light">
      {/* Header */}
      <div className="bg-card shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-success rounded-lg">
              <Pill className="h-6 w-6 text-success-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Pharmacy Management</h1>
              <p className="text-sm text-muted-foreground">
                Welcome, {user?.user_metadata?.full_name || user?.email}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="outline" size="icon">
                  <Settings className="h-4 w-4" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>AI Service Configuration</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="api-key">AI Service API Key</Label>
                    <Input
                      id="api-key"
                      type="password"
                      placeholder="Enter your API key"
                      value={aiApiKey}
                      onChange={(e) => setAiApiKey(e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground">
                      Add your API key to enable AI demand prediction features
                    </p>
                  </div>
                  <Button className="w-full">Save Configuration</Button>
                </div>
              </DialogContent>
            </Dialog>
            <Button variant="outline" onClick={handleSignOut}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Items</p>
                  <p className="text-3xl font-bold text-foreground">{stats.totalItems}</p>
                </div>
                <div className="p-3 bg-primary-light rounded-full">
                  <Package className="h-8 w-8 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Low Stock Items</p>
                  <p className="text-3xl font-bold text-foreground">{stats.lowStock}</p>
                </div>
                <div className="p-3 bg-urgent-light rounded-full">
                  <AlertTriangle className="h-8 w-8 text-urgent" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Urgent Orders</p>
                  <p className="text-3xl font-bold text-foreground">{stats.urgentOrders}</p>
                </div>
                <div className="p-3 bg-urgent-light rounded-full">
                  <Package className="h-8 w-8 text-urgent" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-success to-secondary text-success-foreground cursor-pointer hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">AI Demand Prediction</p>
                  <p className="text-lg font-semibold">View Analytics</p>
                </div>
                <TrendingUp className="h-8 w-8" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Inventory Management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Package className="h-5 w-5 mr-2 text-primary" />
                Inventory Management
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Medication</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {inventory.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center text-muted-foreground">
                        No inventory items
                      </TableCell>
                    </TableRow>
                  ) : (
                    inventory.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">
                          {item.medications?.name || "Unknown"}
                        </TableCell>
                        <TableCell>{item.quantity}</TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              item.quantity <= item.reorder_level
                                ? "destructive"
                                : "outline"
                            }
                          >
                            {item.quantity <= item.reorder_level
                              ? "Low Stock"
                              : "In Stock"}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Urgent Hospital Orders */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-urgent" />
                Urgent Hospital Orders
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Medication</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Urgency</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {urgentOrders.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center text-muted-foreground">
                        No urgent orders
                      </TableCell>
                    </TableRow>
                  ) : (
                    urgentOrders.map((order) => (
                      <TableRow key={order.id}>
                        <TableCell className="font-medium">
                          {order.medications?.name || "Unknown"}
                        </TableCell>
                        <TableCell>{order.quantity}</TableCell>
                        <TableCell>
                          <Badge variant="destructive">{order.urgency}</Badge>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PharmacyDashboard;
