import { Spinner } from "flowbite-react";
import NewChatForm from "../components/NewChatForm";
import dynamic from "next/dynamic";

const Modal = dynamic(() => import("flowbite-react").then((mod) => mod.Modal), {
  ssr: true,
  loading: () => (
    <div className="flex items-center justify-center">
      <Spinner />
    </div>
  ),
});

const ModalBody = dynamic(
  () => import("flowbite-react").then((mod) => mod.ModalBody),
  {
    ssr: true,
    loading: () => (
      <div className="flex items-center justify-center">
        <Spinner />
      </div>
    ),
  }
);

export default function Home() {
  return (
    <>
      <Modal show>
        <ModalBody>
          <NewChatForm />
        </ModalBody>
      </Modal>
    </>
  );
}
