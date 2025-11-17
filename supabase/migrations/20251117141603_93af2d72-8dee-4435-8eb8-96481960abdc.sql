-- Create role enum
CREATE TYPE public.app_role AS ENUM ('patient', 'hospital_staff', 'pharmacy_staff', 'admin');

-- Create profiles table
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  phone TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create user_roles table
CREATE TABLE public.user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  role app_role NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, role)
);

ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- Security definer function to check roles
CREATE OR REPLACE FUNCTION public.has_role(_user_id UUID, _role app_role)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles
    WHERE user_id = _user_id AND role = _role
  )
$$;

-- Create patients table (extended profile info for patients)
CREATE TABLE public.patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
  date_of_birth DATE,
  blood_type TEXT,
  allergies TEXT[],
  emergency_contact TEXT,
  emergency_phone TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;

-- Create medications table
CREATE TABLE public.medications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  dosage_form TEXT,
  manufacturer TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.medications ENABLE ROW LEVEL SECURITY;

-- Create prescriptions table
CREATE TABLE public.prescriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID REFERENCES public.patients(id) ON DELETE CASCADE NOT NULL,
  medication_id UUID REFERENCES public.medications(id) ON DELETE CASCADE NOT NULL,
  prescribed_by UUID REFERENCES auth.users(id),
  dosage TEXT NOT NULL,
  frequency TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE,
  instructions TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'discontinued')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.prescriptions ENABLE ROW LEVEL SECURITY;

-- Create appointments table
CREATE TABLE public.appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID REFERENCES public.patients(id) ON DELETE CASCADE NOT NULL,
  staff_id UUID REFERENCES auth.users(id),
  appointment_date TIMESTAMP WITH TIME ZONE NOT NULL,
  department TEXT NOT NULL,
  reason TEXT,
  status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no-show')),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;

-- Create lab_reports table
CREATE TABLE public.lab_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID REFERENCES public.patients(id) ON DELETE CASCADE NOT NULL,
  test_name TEXT NOT NULL,
  test_date TIMESTAMP WITH TIME ZONE NOT NULL,
  results JSONB,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'reviewed')),
  ordered_by UUID REFERENCES auth.users(id),
  reviewed_by UUID REFERENCES auth.users(id),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.lab_reports ENABLE ROW LEVEL SECURITY;

-- Create inventory table (pharmacy stock)
CREATE TABLE public.inventory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  medication_id UUID REFERENCES public.medications(id) ON DELETE CASCADE NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 0,
  reorder_level INTEGER NOT NULL DEFAULT 50,
  unit_price DECIMAL(10, 2),
  expiry_date DATE,
  batch_number TEXT,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.inventory ENABLE ROW LEVEL SECURITY;

-- Create hospital_orders table
CREATE TABLE public.hospital_orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  medication_id UUID REFERENCES public.medications(id) ON DELETE CASCADE NOT NULL,
  ordered_by UUID REFERENCES auth.users(id) NOT NULL,
  quantity INTEGER NOT NULL,
  urgency TEXT DEFAULT 'normal' CHECK (urgency IN ('normal', 'urgent', 'emergency')),
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'fulfilled', 'cancelled')),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  fulfilled_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.hospital_orders ENABLE ROW LEVEL SECURITY;

-- Trigger function for profile creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, phone)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'phone', '')
  );
  RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- RLS Policies

-- Profiles: Users can view and update their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- User roles: Users can view their own roles
CREATE POLICY "Users can view own roles" ON public.user_roles
  FOR SELECT USING (auth.uid() = user_id);

-- Patients: Patients can view their own data, staff can view all
CREATE POLICY "Patients can view own data" ON public.patients
  FOR SELECT USING (
    auth.uid() = user_id OR 
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

-- Medications: All authenticated users can view
CREATE POLICY "Authenticated users can view medications" ON public.medications
  FOR SELECT TO authenticated USING (true);

-- Hospital staff can manage medications
CREATE POLICY "Staff can manage medications" ON public.medications
  FOR ALL USING (
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'pharmacy_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

-- Prescriptions: Patients can view their own, staff can manage
CREATE POLICY "Patients can view own prescriptions" ON public.prescriptions
  FOR SELECT USING (
    patient_id IN (SELECT id FROM public.patients WHERE user_id = auth.uid()) OR
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

CREATE POLICY "Staff can manage prescriptions" ON public.prescriptions
  FOR ALL USING (
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

-- Appointments: Patients can view their own, staff can manage
CREATE POLICY "Patients can view own appointments" ON public.appointments
  FOR SELECT USING (
    patient_id IN (SELECT id FROM public.patients WHERE user_id = auth.uid()) OR
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

CREATE POLICY "Staff can manage appointments" ON public.appointments
  FOR ALL USING (
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

-- Lab reports: Patients can view their own, staff can manage
CREATE POLICY "Patients can view own lab reports" ON public.lab_reports
  FOR SELECT USING (
    patient_id IN (SELECT id FROM public.patients WHERE user_id = auth.uid()) OR
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

CREATE POLICY "Staff can manage lab reports" ON public.lab_reports
  FOR ALL USING (
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

-- Inventory: Pharmacy staff can manage
CREATE POLICY "Pharmacy staff can manage inventory" ON public.inventory
  FOR ALL USING (
    public.has_role(auth.uid(), 'pharmacy_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

-- Hospital orders: Hospital staff can create, pharmacy staff can manage
CREATE POLICY "Hospital staff can create orders" ON public.hospital_orders
  FOR INSERT WITH CHECK (
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

CREATE POLICY "Staff can view orders" ON public.hospital_orders
  FOR SELECT USING (
    public.has_role(auth.uid(), 'hospital_staff') OR
    public.has_role(auth.uid(), 'pharmacy_staff') OR
    public.has_role(auth.uid(), 'admin')
  );

CREATE POLICY "Pharmacy staff can manage orders" ON public.hospital_orders
  FOR UPDATE USING (
    public.has_role(auth.uid(), 'pharmacy_staff') OR
    public.has_role(auth.uid(), 'admin')
  );