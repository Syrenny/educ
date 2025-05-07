// Modal.tsx
import { useEffect, useRef, ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'

interface ModalProps {
	isOpen: boolean
	onClose: () => void
	width?: string
	closeButton?: boolean
	children: ReactNode
}

export default function Modal({
	isOpen,
	onClose,
	width = 'max-w-sm',
	closeButton = false,
	children,
}: ModalProps) {
	const backdropRef = useRef<HTMLDivElement>(null)
	const modalRef = useRef<HTMLDivElement>(null)

	useEffect(() => {
		if (!isOpen) return

		// Add inert to #app
		const app = document.getElementById('app')
		app?.setAttribute('inert', 'true')

		// Focus modal on open
		modalRef.current?.focus()

		const handleKeydown = (e: KeyboardEvent) => {
			if (e.key === 'Escape') {
				e.preventDefault()
				onClose()
			}
		}

		document.addEventListener('keydown', handleKeydown)
		return () => {
			app?.removeAttribute('inert')
			document.removeEventListener('keydown', handleKeydown)
		}
	}, [isOpen, onClose])

	const handleBackdropClick = (e: React.MouseEvent) => {
		if (window.getSelection()?.toString()) return
		if (e.target === backdropRef.current) {
			onClose()
		}
	}

	return createPortal(
		<AnimatePresence>
			{isOpen && (
				<motion.div
					role='presentation'
					tabIndex={-1}
					ref={backdropRef}
					onClick={handleBackdropClick}
					className='fixed inset-0 z-40 flex items-center justify-center bg-black/80 backdrop-blur-sm dark:bg-black/50'
					initial={{ opacity: 0 }}
					animate={{ opacity: 1 }}
					exit={{ opacity: 0 }}
					transition={{ ease: 'easeOut', duration: 0.3 }}
				>
					<motion.div
						role='dialog'
						tabIndex={-1}
						ref={modalRef}
						onClick={e => e.stopPropagation()}
						className={`relative mx-auto max-h-[95dvh] max-w-[90dvw] overflow-y-auto overflow-x-hidden rounded-2xl bg-white shadow-2xl outline-none ${width}`}
						initial={{ y: 100, opacity: 0 }}
						animate={{ y: 0, opacity: 1 }}
						exit={{ y: 100, opacity: 0 }}
						transition={{
							type: 'spring',
							damping: 25,
							stiffness: 300,
						}}
					>
						{closeButton && (
							<button
								className='absolute right-4 top-4 z-50'
								onClick={onClose}
							>
								<X className='w-6 h-6 text-gray-700' />
							</button>
						)}
						{children}
					</motion.div>
				</motion.div>
			)}
		</AnimatePresence>,
		document.body
	)
}
