"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import { Brain, ArrowRight, ArrowLeft } from "lucide-react";

interface OnboardingData {
  role: string;
  patient_name: string;
  caregiver_name: string;
  diagnosis: string;
  doctor_name: string;
  clinic_name: string;
  medications: { drug_name: string; dosage: string; cycle_type: string; cycle_start_date: string }[];
  appointment_date: string;
  appointment_type: string;
}

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState<OnboardingData>({
    role: "",
    patient_name: "",
    caregiver_name: "",
    diagnosis: "",
    doctor_name: "",
    clinic_name: "",
    medications: [{ drug_name: "", dosage: "", cycle_type: "", cycle_start_date: "" }],
    appointment_date: "",
    appointment_type: "",
  });

  const update = (field: string, value: string) => {
    setData((prev) => ({ ...prev, [field]: value }));
  };

  const updateMed = (index: number, field: string, value: string) => {
    setData((prev) => {
      const meds = [...prev.medications];
      meds[index] = { ...meds[index], [field]: value };
      return { ...prev, medications: meds };
    });
  };

  const addMed = () => {
    setData((prev) => ({
      ...prev,
      medications: [...prev.medications, { drug_name: "", dosage: "", cycle_type: "", cycle_start_date: "" }],
    }));
  };

  const removeMed = (index: number) => {
    setData((prev) => ({
      ...prev,
      medications: prev.medications.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async () => {
    setSaving(true);
    try {
      // Create user
      const user = await fetchApi<{ id: number }>("/api/users", {
        method: "POST",
        body: JSON.stringify({
          role: data.role,
          patient_name: data.patient_name || null,
          caregiver_name: data.caregiver_name || null,
        }),
      });

      const userId = user.id;
      localStorage.setItem("neuronav_user_id", userId.toString());

      // Update user with diagnosis/doctor/clinic
      await fetchApi(`/api/users/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({
          diagnosis: data.diagnosis || null,
          doctor_name: data.doctor_name || null,
          clinic_name: data.clinic_name || null,
          onboarding_complete: true,
        }),
      });

      // Save medications
      for (const med of data.medications) {
        if (!med.drug_name.trim()) continue;

        // Auto-detect drug key and cycle type
        const drugLower = med.drug_name.toLowerCase();
        let drug_key = "";
        let cycle_type = med.cycle_type || "";

        if (drugLower.includes("tmz") || drugLower.includes("temozolomide")) {
          drug_key = "tmz";
          if (!cycle_type) cycle_type = "tmz28";
        } else if (drugLower.includes("etoposide")) {
          drug_key = "etoposide";
          if (!cycle_type) cycle_type = "etoposide28";
        } else if (drugLower.includes("bevacizumab") || drugLower.includes("avastin")) {
          drug_key = "bevacizumab";
        } else if (drugLower.includes("lomustine") || drugLower.includes("ccnu")) {
          drug_key = "lomustine";
        } else if (drugLower.includes("vorasidenib")) {
          drug_key = "vorasidenib";
        }

        // Use the chat endpoint to save medication via tool call — or save directly
        await fetchApi("/api/onboarding/medication", {
          method: "POST",
          body: JSON.stringify({
            user_id: userId,
            drug_name: med.drug_name,
            drug_key,
            dosage: med.dosage || null,
            cycle_type: cycle_type || null,
            cycle_start_date: med.cycle_start_date || null,
          }),
        });
      }

      // Save appointment if provided
      if (data.appointment_date) {
        await fetchApi("/api/appointments", {
          method: "POST",
          body: JSON.stringify({
            user_id: userId,
            appointment_date: data.appointment_date,
            appointment_type: data.appointment_type || null,
            doctor_name: data.doctor_name || null,
          }),
        });
      }

      router.push("/chat");
    } catch (error) {
      console.error("Onboarding error:", error);
      setSaving(false);
    }
  };

  const steps = [
    // Step 0: Role
    <div key="role" className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Welcome to NeuroNav</h2>
      <p className="text-gray-500">Let&apos;s get to know you so we can provide the best support.</p>
      <div className="space-y-3 pt-4">
        <button
          onClick={() => { update("role", "patient"); setStep(1); }}
          className={`w-full py-4 px-6 rounded-xl text-left border-2 transition-colors ${
            data.role === "patient" ? "border-indigo-600 bg-indigo-50" : "border-gray-200 hover:border-gray-300"
          }`}
        >
          <p className="font-medium text-gray-900">I am a patient</p>
          <p className="text-sm text-gray-500">I have been diagnosed with a brain tumour</p>
        </button>
        <button
          onClick={() => { update("role", "caregiver"); setStep(1); }}
          className={`w-full py-4 px-6 rounded-xl text-left border-2 transition-colors ${
            data.role === "caregiver" ? "border-indigo-600 bg-indigo-50" : "border-gray-200 hover:border-gray-300"
          }`}
        >
          <p className="font-medium text-gray-900">I am a caregiver</p>
          <p className="text-sm text-gray-500">I am caring for someone with a brain tumour</p>
        </button>
      </div>
    </div>,

    // Step 1: Names
    <div key="names" className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Tell us about yourself</h2>
      {data.role === "caregiver" ? (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Your name</label>
            <input
              type="text"
              value={data.caregiver_name}
              onChange={(e) => update("caregiver_name", e.target.value)}
              placeholder="e.g. Sarah"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Patient&apos;s name</label>
            <input
              type="text"
              value={data.patient_name}
              onChange={(e) => update("patient_name", e.target.value)}
              placeholder="e.g. Michael"
              className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </>
      ) : (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Your name</label>
          <input
            type="text"
            value={data.patient_name}
            onChange={(e) => update("patient_name", e.target.value)}
            placeholder="e.g. Michael"
            className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
      )}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosis</label>
        <input
          type="text"
          value={data.diagnosis}
          onChange={(e) => update("diagnosis", e.target.value)}
          placeholder="e.g. Glioblastoma (GBM), Grade IV"
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
    </div>,

    // Step 2: Care team
    <div key="care-team" className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Your care team</h2>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Oncologist / Doctor name</label>
        <input
          type="text"
          value={data.doctor_name}
          onChange={(e) => update("doctor_name", e.target.value)}
          placeholder="e.g. Dr. Patel"
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Clinic / Hospital</label>
        <input
          type="text"
          value={data.clinic_name}
          onChange={(e) => update("clinic_name", e.target.value)}
          placeholder="e.g. Sunnybrook Neuro-Oncology"
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
    </div>,

    // Step 3: Medications
    <div key="medications" className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Current medications</h2>
      <p className="text-sm text-gray-500">Add any brain tumour medications currently being taken.</p>
      {data.medications.map((med, i) => (
        <div key={i} className="p-4 rounded-xl border border-gray-200 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Medication {i + 1}</span>
            {data.medications.length > 1 && (
              <button onClick={() => removeMed(i)} className="text-xs text-red-500 hover:text-red-700">Remove</button>
            )}
          </div>
          <input
            type="text"
            value={med.drug_name}
            onChange={(e) => updateMed(i, "drug_name", e.target.value)}
            placeholder="Drug name (e.g. Temozolomide / TMZ)"
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <input
            type="text"
            value={med.dosage}
            onChange={(e) => updateMed(i, "dosage", e.target.value)}
            placeholder="Dosage (e.g. 200mg daily)"
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <div>
            <label className="block text-xs text-gray-500 mb-1">Cycle start date (if on a treatment cycle)</label>
            <input
              type="date"
              value={med.cycle_start_date}
              onChange={(e) => updateMed(i, "cycle_start_date", e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>
      ))}
      <button
        onClick={addMed}
        className="w-full py-2.5 px-4 rounded-lg border-2 border-dashed border-gray-300 text-sm text-gray-500 hover:border-gray-400 hover:text-gray-700 transition-colors"
      >
        + Add another medication
      </button>
    </div>,

    // Step 4: Upcoming appointment
    <div key="appointment" className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Next appointment</h2>
      <p className="text-sm text-gray-500">Optional — you can add this later too.</p>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Appointment date</label>
        <input
          type="date"
          value={data.appointment_date}
          onChange={(e) => update("appointment_date", e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Appointment type</label>
        <select
          value={data.appointment_type}
          onChange={(e) => update("appointment_type", e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        >
          <option value="">Select type...</option>
          <option value="Oncologist follow-up">Oncologist follow-up</option>
          <option value="MRI">MRI scan</option>
          <option value="Bloodwork">Bloodwork</option>
          <option value="Radiation">Radiation</option>
          <option value="Surgery consult">Surgery consult</option>
          <option value="Other">Other</option>
        </select>
      </div>
    </div>,
  ];

  const canNext =
    (step === 0 && data.role) ||
    (step === 1 && (data.patient_name || data.caregiver_name)) ||
    step === 2 ||
    step === 3 ||
    step === 4;

  const isLast = step === steps.length - 1;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="max-w-lg w-full mx-4">
        <div className="flex items-center justify-center mb-8">
          <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center mr-3">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">NeuroNav</h1>
        </div>

        {/* Progress */}
        <div className="flex gap-1.5 mb-6">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 flex-1 rounded-full transition-colors ${
                i <= step ? "bg-indigo-600" : "bg-gray-200"
              }`}
            />
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          {steps[step]}

          <div className="flex justify-between mt-8">
            {step > 0 ? (
              <button
                onClick={() => setStep(step - 1)}
                className="flex items-center gap-2 px-4 py-2.5 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
            ) : (
              <div />
            )}

            {step > 0 && (
              <button
                onClick={isLast ? handleSubmit : () => setStep(step + 1)}
                disabled={!canNext || saving}
                className="flex items-center gap-2 px-6 py-2.5 text-sm rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-indigo-300 transition-colors"
              >
                {saving ? "Saving..." : isLast ? "Start chatting" : "Next"}
                {!isLast && !saving && <ArrowRight className="w-4 h-4" />}
              </button>
            )}
          </div>
        </div>

        <p className="text-xs text-gray-400 text-center mt-6">
          For demo purposes only. Not a substitute for professional medical advice.
        </p>
      </div>
    </div>
  );
}
