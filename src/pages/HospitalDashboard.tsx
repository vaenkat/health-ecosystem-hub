import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { Stethoscope, Users, Calendar, FileText, LogOut } from "lucide-react";

const HospitalDashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ patients: 0, appointments: 0, pendingReports: 0 });
  const [recentAppointments, setRecentAppointments] = useState<any[]>([]);
  const [pendingReports, setPendingReports] = useState<any[]>([]);

  useEffect(() => {
    checkUser();
    fetchData();
  }, []);

  const checkUser = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      navigate("/auth/hospital");
      return;
    }
    setUser(session.user);
  };

  const fetchData = async () => {
    try {
      // Fetch stats
      const { count: patientsCount } = await supabase
        .from("patients")
        .select("*", { count: "exact", head: true });

      const { count: appointmentsCount } = await supabase
        .from("appointments")
        .select("*", { count: "exact", head: true })
        .eq("status", "scheduled");

      const { count: reportsCount } = await supabase
        .from("lab_reports")
        .select("*", { count: "exact", head: true })
        .eq("status", "pending");

      setStats({
        patients: patientsCount || 0,
        appointments: appointmentsCount || 0,
        pendingReports: reportsCount || 0,
      });

      // Fetch recent appointments
      const { data: appointmentsData } = await supabase
        .from("appointments")
        .select("*, patients(user_id), profiles!inner(full_name)")
        .eq("status", "scheduled")
        .order("appointment_date", { ascending: true })
        .limit(5);

      setRecentAppointments(appointmentsData || []);

      // Fetch pending lab reports
      const { data: reportsData } = await supabase
        .from("lab_reports")
        .select("*, patients(user_id), profiles!inner(full_name)")
        .eq("status", "pending")
        .order("test_date", { ascending: false })
        .limit(5);

      setPendingReports(reportsData || []);
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
    <div className="min-h-screen bg-gradient-to-br from-secondary-light via-background to-primary-light">
      {/* Header */}
      <div className="bg-card shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-secondary rounded-lg">
              <Stethoscope className="h-6 w-6 text-secondary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Hospital Management</h1>
              <p className="text-sm text-muted-foreground">
                Welcome, {user?.user_metadata?.full_name || user?.email}
              </p>
            </div>
          </div>
          <Button variant="outline" onClick={handleSignOut}>
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Current Patients</p>
                  <p className="text-3xl font-bold text-foreground">{stats.patients}</p>
                </div>
                <div className="p-3 bg-primary-light rounded-full">
                  <Users className="h-8 w-8 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Scheduled Appointments</p>
                  <p className="text-3xl font-bold text-foreground">{stats.appointments}</p>
                </div>
                <div className="p-3 bg-secondary-light rounded-full">
                  <Calendar className="h-8 w-8 text-secondary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Pending Lab Reports</p>
                  <p className="text-3xl font-bold text-foreground">{stats.pendingReports}</p>
                </div>
                <div className="p-3 bg-urgent-light rounded-full">
                  <FileText className="h-8 w-8 text-urgent" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Appointment Schedule */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="h-5 w-5 mr-2 text-secondary" />
                Appointment Schedules
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Patient</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Date & Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentAppointments.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center text-muted-foreground">
                        No scheduled appointments
                      </TableCell>
                    </TableRow>
                  ) : (
                    recentAppointments.map((appointment) => (
                      <TableRow key={appointment.id}>
                        <TableCell className="font-medium">
                          {appointment.profiles?.full_name || "Unknown"}
                        </TableCell>
                        <TableCell>{appointment.department}</TableCell>
                        <TableCell className="text-sm">
                          {new Date(appointment.appointment_date).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Pending Lab Reports */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-urgent" />
                Pending Lab Reports
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Patient</TableHead>
                    <TableHead>Test Name</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pendingReports.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center text-muted-foreground">
                        No pending reports
                      </TableCell>
                    </TableRow>
                  ) : (
                    pendingReports.map((report) => (
                      <TableRow key={report.id}>
                        <TableCell className="font-medium">
                          {report.profiles?.full_name || "Unknown"}
                        </TableCell>
                        <TableCell>{report.test_name}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{report.status}</Badge>
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

export default HospitalDashboard;
