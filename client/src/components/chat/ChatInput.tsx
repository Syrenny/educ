import React, { useState } from 'react'

type ChatInputProps = {
	disabled: boolean
	onSubmit: () => void
	onChange: (message: string) => void
}

const ChatInput: React.FC<ChatInputProps> = ({ disabled, onSubmit, onChange }) => {
   	const [message, setMessage] = useState('')

    const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault()
		setMessage('')
		onSubmit()
	}

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		setMessage(e.target.value)
		onChange(e.target.value)
	}

    const handleKeydown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (event.key === 'Enter' && !event.shiftKey && message.trim() !== '') {
			handleSubmit(event)
		}
	}

	return (
		<div className='w-full'>
			<form
				aria-label={undefined}
				onSubmit={handleSubmit}
				className='relative flex w-full max-w-4xl flex-1 items-center rounded-xl border bg-gray-100 dark:border-gray-600 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
			>
				<div className='flex w-full flex-1 rounded-xl border-none bg-transparent'>
					<div className='flex min-h-full flex-1 flex-col'>
						<textarea
							autoFocus
							disabled={disabled}
							value={message}
							rows={3}
							className='max-h-[4lh] w-full resize-none overflow-y-auto overflow-x-hidden border-0 bg-transparent px-2.5 py-2.5 outline-none focus:ring-0 focus-visible:ring-0 max-sm:text-[16px] sm:px-3'
							onChange={handleChange}
							onKeyDown={handleKeydown}
                            placeholder='Спросите что-нибудь...'
						></textarea>
					</div>
					<button
						className='cursor-pointer btn absolute bottom-2 right-2 size-7 self-end rounded-full border bg-white text-black shadow transition-none enabled:hover:bg-white enabled:hover:shadow-inner disabled:opacity-60 dark:border-gray-600 dark:bg-gray-900 dark:text-white dark:hover:enabled:bg-black'
						disabled={disabled || message.trim() === ''}
						type='submit'
						aria-label='Send message'
					>
						<svg
							width='1em'
							height='1em'
							viewBox='0 0 32 32'
							fill='none'
							xmlns='http://www.w3.org/2000/svg'
							className='justify-self-center'
						>
							<path
								fillRule='evenodd'
								clipRule='evenodd'
								d='M17.0606 4.23197C16.4748 3.64618 15.525 3.64618 14.9393 4.23197L5.68412 13.4871C5.09833 14.0729 5.09833 15.0226 5.68412 15.6084C6.2699 16.1942 7.21965 16.1942 7.80544 15.6084L14.4999 8.91395V26.7074C14.4999 27.5359 15.1715 28.2074 15.9999 28.2074C16.8283 28.2074 17.4999 27.5359 17.4999 26.7074V8.91395L24.1944 15.6084C24.7802 16.1942 25.7299 16.1942 26.3157 15.6084C26.9015 15.0226 26.9015 14.0729 26.3157 13.4871L17.0606 4.23197Z'
								fill='currentColor'
							/>
						</svg>
					</button>
				</div>
			</form>
		</div>
	)
}

export default ChatInput
