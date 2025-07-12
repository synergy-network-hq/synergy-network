import React, { useEffect, useRef } from "react";
import ReactDOM from "react-dom";

// For accessibility: trap focus inside modal
function useFocusTrap(ref, isOpen) {
  useEffect(() => {
    if (!isOpen || !ref.current) return;
    const node = ref.current;
    const focusable = node.querySelectorAll(
      "button, [href], input, textarea, select, [tabindex]:not([tabindex='-1'])"
    );
    if (focusable.length) focusable[0].focus();
    const handleTab = e => {
      if (e.key !== "Tab") return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) {
          last.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === last) {
          first.focus();
          e.preventDefault();
        }
      }
    };
    node.addEventListener("keydown", handleTab);
    return () => node.removeEventListener("keydown", handleTab);
  }, [isOpen, ref]);
}

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  width = 480,
  hideClose = false,
}) {
  const modalRef = useRef(null);

  // Close on ESC key
  useEffect(() => {
    if (!isOpen) return;
    function handleEsc(e) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

  useFocusTrap(modalRef, isOpen);

  if (!isOpen) return null;

  const modalJSX = (
    <div
      className="modal-overlay synergy-modal-overlay"
      onClick={onClose}
      tabIndex={-1}
      aria-modal="true"
      role="dialog"
    >
      <div
        className="modal synergy-modal"
        ref={modalRef}
        style={{
          minWidth: "900px",
          width: "900px",
          maxWidth: "95vw",
          margin: "40px auto",
          height: "600px",
          borderRadius: 25,
          boxShadow: "0 8px 48px 0 #000c",
          fontFamily: "Inter, sans-serif",
        }}
        onClick={e => e.stopPropagation()}
        tabIndex={0}
      >
        <div className="modal-header synergy-modal-header">
          {/* <h3 className="modal-title synergy-modal-title">{title}</h3> */}
          {!hideClose && (
            <button
              className="modal-close synergy-modal-close"
              onClick={onClose}
              aria-label="Close modal"
            >
              ×
            </button>
          )}
        </div>
        <div className="modal-content synergy-modal-content">{children}</div>
      </div>
    </div>
  );

  // *** Render into <body> via Portal ***
  return ReactDOM.createPortal(modalJSX, document.body);
}
