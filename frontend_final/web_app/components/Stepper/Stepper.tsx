import React from 'react';

interface Step {
  title: string;
  icon: string;
}

interface StepperProps {
  steps: Step[];
  activeStep: number;
}

const Stepper: React.FC<StepperProps> = ({ steps, activeStep }) => (
  <ol className="flex items-center w-full mb-8">
    {steps.map((step, index) => (
      <li key={index} className={`flex w-full items-center ${index < steps.length - 1 ? 'after:content-[\'\'] after:w-full after:h-1 after:border-b after:border-gray-100 after:border-4 after:inline-block dark:after:border-gray-700' : ''} ${index < activeStep ? 'text-blue-600 dark:text-blue-500' : 'text-gray-500 dark:text-gray-300'}`}>
        <span className={`flex items-center justify-center w-10 h-10 ${index <= activeStep ? 'bg-blue-100 dark:bg-blue-800' : 'bg-gray-100 dark:bg-gray-700'} rounded-full lg:h-12 lg:w-12 shrink-0`}>
          <svg className={`w-3.5 h-3.5 ${index <= activeStep ? 'text-blue-600 dark:text-blue-300' : 'text-gray-500 dark:text-gray-100'} lg:w-4 lg:h-4`} aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
            <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={step.icon}/>
          </svg>
        </span>
        <span className="ml-2 text-sm">{step.title}</span>
      </li>
    ))}
  </ol>
);

export default Stepper;