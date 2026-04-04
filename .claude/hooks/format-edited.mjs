import { execSync } from "child_process";

let input = "";
process.stdin.on("data", (d) => (input += d));
process.stdin.on("end", () => {
  const data = JSON.parse(input);
  const fp = data?.tool_input?.file_path ?? "";

  if (fp.includes("/backend/")) {
    execSync("make format-backend", { stdio: "inherit" });
  } else if (fp.includes("/frontend/")) {
    execSync("make format-frontend", { stdio: "inherit" });
  }
});
