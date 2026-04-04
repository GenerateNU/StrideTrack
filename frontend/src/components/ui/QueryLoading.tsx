import Lottie from "lottie-react";
import runnerAnimation from "@/assets/runner-animation.json";

export function QueryLoading() {
  return (
    <div className="flex h-full w-full items-center justify-center">
      <Lottie
        animationData={runnerAnimation}
        loop={true}
        style={{ height: 128, width: 128 }}
      />
    </div>
  );
}
