import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { Pill, Calendar, Activity, MessageCircle, LogOut } from "lucide-react";

const PatientDashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [prescriptions, setPrescriptions] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);

  useEffect(() => {
    checkUser();
    fetchData();
  }, []);

  const checkUser = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      navigate("/auth/patient");
      return;
    }
    setUser(session.user);
  };

  const fetchData = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Fetch patient record
      const { data: patientData } = await supabase
        .from("patients")
        .select("id")
        .eq("user_id", user.id)
        .single();

      if (patientData) {
        // Fetch prescriptions
        const { data: prescriptionsData } = await supabase
          .from("prescriptions")
          .select("*, medications(*)")
          .eq("patient_id", patientData.id)
          .eq("status", "active")
          .limit(5);

        setPrescriptions(prescriptionsData || []);

        // Fetch appointments
        const { data: appointmentsData } = await supabase
          .from("appointments")
          .select("*")
          .eq("patient_id", patientData.id)
          .gte("appointment_date", new Date().toISOString())
          .order("appointment_date", { ascending: true })
          .limit(5);

        setAppointments(appointmentsData || []);
      }
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
    <div className="min-h-screen bg-gradient-to-br from-primary-light via-background to-secondary-light">
      {/* Header */}
      <div className="bg-card shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary rounded-lg">
              <Activity className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Patient Portal</h1>
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
        {/* Quick Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Medications</p>
                  <p className="text-3xl font-bold text-foreground">{prescriptions.length}</p>
                </div>
                <div className="p-3 bg-primary-light rounded-full">
                  <Pill className="h-8 w-8 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Upcoming Appointments</p>
                  <p className="text-3xl font-bold text-foreground">{appointments.length}</p>
                </div>
                <div className="p-3 bg-secondary-light rounded-full">
                  <Calendar className="h-8 w-8 text-secondary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-primary to-secondary text-primary-foreground cursor-pointer hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">AI Health Assistant</p>
                  <p className="text-lg font-semibold">Chat Now</p>
                </div>
                <MessageCircle className="h-8 w-8" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* My Medications */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Pill className="h-5 w-5 mr-2 text-primary" />
                My Medications
              </CardTitle>
            </CardHeader>
            <CardContent>
              {prescriptions.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">
                  No active medications
                </p>
              ) : (
                <div className="space-y-3">
                  {prescriptions.map((prescription) => (
                    <div
                      key={prescription.id}
                      className="p-4 bg-muted rounded-lg"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-foreground">
                          {prescription.medications?.name}
                        </h4>
                        <Badge variant="outline">{prescription.status}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {prescription.dosage} - {prescription.frequency}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {prescription.instructions}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Upcoming Appointments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="h-5 w-5 mr-2 text-secondary" />
                Upcoming Appointments
              </CardTitle>
            </CardHeader>
            <CardContent>
              {appointments.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">
                  No upcoming appointments
                </p>
              ) : (
                <div className="space-y-3">
                  {appointments.map((appointment) => (
                    <div
                      key={appointment.id}
                      className="p-4 bg-muted rounded-lg"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-foreground">
                          {appointment.department}
                        </h4>
                        <Badge>{appointment.status}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {new Date(appointment.appointment_date).toLocaleString()}
                      </p>
                      {appointment.reason && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {appointment.reason}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;
