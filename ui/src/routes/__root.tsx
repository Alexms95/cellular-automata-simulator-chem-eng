import { InfoCircledIcon } from "@radix-ui/react-icons";
import {
  createRootRoute,
  Link,
  Outlet,
  redirect,
} from "@tanstack/react-router";

export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />
      <footer className="fixed bottom-0 left-0 w-full bg-zinc-800 text-white text-xs text-center p-2 flex items-center justify-evenly">
        <p>&copy; {new Date().getFullYear()} Cellular Automata Simulator</p>
        <div className="flex items-center">
          <InfoCircledIcon className="mr-1" />
          <Link to="/about">About this project</Link>
        </div>
      </footer>
    </>
  ),
  beforeLoad: () => {
    if (location.pathname === "/") {
      throw redirect({ to: "/simulations" });
    }
  },
});
