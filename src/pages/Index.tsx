import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Activity, Users, Pill, Stethoscope } from "lucide-react";

const Index = () => {
  const navigate = useNavigate();
  const [selectedRole, setSelectedRole] = useState<string | null>(null);

  const roles = [
    {
      id: "patient",
      title: "Patient Portal",
      description: "Access your medical records, appointments, and medications",
      icon: Activity,
      color: "primary",
      route: "/auth/patient",
    },
    {
      id: "hospital",
      title: "Hospital Staff",
      description: "Manage patients, appointments, and lab reports",
      icon: Stethoscope,
      color: "secondary",
      route: "/auth/hospital",
    },
    {
      id: "pharmacy",
      title: "Pharmacy Staff",
      description: "Manage inventory, orders, and AI demand prediction",
      icon: Pill,
      color: "success",
      route: "/auth/pharmacy",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-light via-background to-secondary-light">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center mb-6">
            <div className="p-4 bg-primary rounded-2xl shadow-lg">
              <Users className="h-12 w-12 text-primary-foreground" />
            </div>
          </div>
          <h1 className="text-5xl font-bold text-foreground mb-4">
            Healthcare Management System
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Comprehensive digital ecosystem for integrated hospital and pharmacy management
          </p>
        </div>

        {/* Role Selection Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {roles.map((role) => {
            const Icon = role.icon;
            return (
              <Card
                key={role.id}
                className={`p-8 cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-105 ${
                  selectedRole === role.id ? `ring-4 ring-${role.color}` : ""
                }`}
                onClick={() => setSelectedRole(role.id)}
              >
                <div className="text-center space-y-6">
                  <div className={`mx-auto p-6 bg-${role.color}-light rounded-full w-fit`}>
                    <Icon className={`h-12 w-12 text-${role.color}`} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-foreground mb-2">
                      {role.title}
                    </h3>
                    <p className="text-muted-foreground">
                      {role.description}
                    </p>
                  </div>
                  <Button
                    className="w-full"
                    variant={selectedRole === role.id ? "default" : "outline"}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(role.route);
                    }}
                  >
                    Continue as {role.title.split(" ")[0]}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Features Section */}
        <div className="mt-24 text-center">
          <h2 className="text-3xl font-bold text-foreground mb-12">
            Powered by Advanced Technology
          </h2>
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="p-6 bg-card rounded-xl shadow-card">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="font-semibold text-lg mb-2">AI Integration</h3>
              <p className="text-sm text-muted-foreground">
                Smart chatbots and demand prediction
              </p>
            </div>
            <div className="p-6 bg-card rounded-xl shadow-card">
              <div className="text-4xl mb-4">🔒</div>
              <h3 className="font-semibold text-lg mb-2">Secure & Compliant</h3>
              <p className="text-sm text-muted-foreground">
                HIPAA-compliant data protection
              </p>
            </div>
            <div className="p-6 bg-card rounded-xl shadow-card">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="font-semibold text-lg mb-2">Real-time Updates</h3>
              <p className="text-sm text-muted-foreground">
                Instant synchronization across platforms
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
