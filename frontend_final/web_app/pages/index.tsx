import React, { useState } from 'react';
import Navigation from '../components/Layout/Navigation';
import Header from '../components/Layout/Header';
import ProgressBar from '../components/ProgressBar';
import AddDocumentation from '../components/AddDocumentation';
import BackButton from '../components/BackButton';

const Home: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const steps = [
    { id: '01', name: 'Add Documentation', status: 'current' as const },
    { id: '02', name: 'Test Chatbot', status: 'upcoming' as const },
    { id: '03', name: 'Get Embed Code', status: 'upcoming' as const },
  ];

  const updateStepStatus = (newActiveStep: number) => {
    return steps.map((step, index) => ({
      ...step,
      status: index === newActiveStep 
        ? 'current' 
        : index < newActiveStep 
          ? 'complete' 
          : 'upcoming'
    })) as typeof steps;
  };

  const [currentSteps, setCurrentSteps] = useState(steps);

  const handleNext = () => {
    const newActiveStep = activeStep + 1;
    setActiveStep(newActiveStep);
    setCurrentSteps(updateStepStatus(newActiveStep));
  };

  const handleBack = () => {
    if (activeStep > 0) {
      const newActiveStep = activeStep - 1;
      setActiveStep(newActiveStep);
      setCurrentSteps(updateStepStatus(newActiveStep));
    }
  };

  return (
    <div className="min-h-full bg-gray-100">
      <Navigation />
      <Header />
      <main className="py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <ProgressBar steps={currentSteps} />
          </div>
          <div className="bg-white shadow sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              {activeStep === 0 && <AddDocumentation onNext={handleNext} />}
              {activeStep === 1 && (
                <>
                  {/* Test Chatbot content will go here */}
                  <div className="flex justify-between mt-6">
                    <BackButton onClick={handleBack} />
                    <button
                      onClick={handleNext}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Next
                    </button>
                  </div>
                </>
              )}
              {activeStep === 2 && (
                <>
                  {/* Get Embed Code content will go here */}
                  <div className="flex justify-between mt-6">
                    <BackButton onClick={handleBack} />
                    <button
                      onClick={() => {/* Handle finish action */}}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Finish
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;