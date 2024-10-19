import { Modal } from "npm:flowbite-react";
import NewChatForm from "../components/NewChatForm";

export default function Home() {
  return (
    <>
      <Modal show>
        <Modal.Body>
          <NewChatForm />
        </Modal.Body>
      </Modal>
    </>
  );
}
