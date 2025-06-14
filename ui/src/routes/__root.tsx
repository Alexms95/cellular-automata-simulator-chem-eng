import { InfoCircledIcon } from "@radix-ui/react-icons";
import {
  createRootRoute,
  Link,
  Outlet,
  redirect,
} from "@tanstack/react-router";

export const Route = createRootRoute({
  component: () => (
    <div className="min-h-screen p-8 bg-zinc-100 dark:bg-zinc-900">
      <Outlet />
      <footer className="fixed bottom-0 left-0 w-full bg-zinc-800 text-white dark:text-zinc-900 dark:bg-white text-xs text-center p-2 flex items-center justify-evenly">
        <p>&copy; {new Date().getFullYear()} Cellular Automata Simulator</p>
        <div className="flex items-center">
          <InfoCircledIcon className="mr-1" />
          <Link to="/about">About this project</Link>
        </div>
      </footer>
    </div>
  ),
  beforeLoad: () => {
    if (location.pathname === "/") {
      throw redirect({ to: "/simulations" });
    }
  },
});
