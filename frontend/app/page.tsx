import DemoApp from "../components/DemoApp";
import { getDemoData } from "../lib/demo-data";

export default function Home() {
  return <DemoApp data={getDemoData()} />;
}
