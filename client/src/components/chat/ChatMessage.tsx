import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { v4 as uuidv4 } from 'uuid'
import { Action, type Message } from '../../types'
import IconLoading from '../icons/IconLoading'
import ChunkItem from './ChunkItem'

interface ChatMessageProps {
	loading: boolean
	message: Message
}

const ChatMessage = ({ loading, message }: ChatMessageProps) => {
	const [isOpen, setIsOpen] = useState(false)

	const translate: Record<Action, string> = {
		[Action.Translate]: 'Перевод',
		[Action.Explain]: 'Объяснение',
		[Action.Default]: '',
		[Action.Ask]: '',
	}

	return (
		<>
			{message.is_user ? (
				<div
					className='group relative w-full items-start justify-start gap-4 max-sm:text-sm'
					data-message-id={uuidv4()}
					data-message-type='user'
					role='presentation'
				>
					<div className='flex w-full flex-col gap-2'>
						<div className='flex w-full flex-row flex-nowrap'>
							<div className='disabled w-full appearance-none whitespace-break-spaces text-wrap break-words bg-inherit px-5 py-3.5 text-gray-700 dark:text-gray-400'>
								{message.content ? (
									message.content.trim()
								) : (
									<div>
										<button
											className='py-1.5 mt-4 flex w-full items-center justify-between text-left'
											onClick={() => setIsOpen(!isOpen)}
										>
											<span className='pl-0.5 italic ml-1.5'>
												{translate[message.action]}
											</span>
											<span>{isOpen ? '▲' : '▼'}</span>
										</button>
										<div
											className={`${
												isOpen ? '' : 'cursor-pointer'
											} relative min-h-[calc(2rem+theme(spacing[3.5])*2)] min-w-[60px] break-words rounded-2xl px-5 py-3.5 prose-pre:my-2 dark:from-gray-800/40 overflow-hidden`}
											onClick={() => setIsOpen(true)}
										>
											<div
												className={
													isOpen
														? ''
														: 'line-clamp-[3]'
												}
											>
												{message.snippet?.trim()}
											</div>

											{!isOpen && (
												<div className='pointer-events-none absolute bottom-0 left-0 h-20 w-full bg-gradient-to-t from-white dark:from-gray-900 to-transparent  rounded-2xl' />
											)}
										</div>
									</div>
								)}
							</div>
						</div>
					</div>
				</div>
			) : (
				<div
					className='group relative -mb-4 flex items-start justify-start gap-4 pb-4 leading-relaxed'
					data-message-id={uuidv4()}
					data-message-role='assistant'
					role='presentation'
				>
					<div className='relative min-h-[calc(2rem+theme(spacing[3.5])*2)] min-w-[60px] break-words rounded-2xl border border-gray-200 bg-gradient-to-br from-gray-50 px-5 py-3.5 text-gray-600 prose-pre:my-2 dark:border-gray-800 dark:from-gray-800/40 dark:text-gray-300'>
						{loading && message.content.length === 0 ? (
							<IconLoading classNames='loading inline ml-2 first:ml-0' />
						) : (
							<div className='prose max-w-none dark:prose-invert max-sm:prose-sm prose-headings:font-semibold prose-h1:text-lg prose-h2:text-base prose-h3:text-base prose-pre:bg-gray-800 dark:prose-pre:bg-gray-900'>
								<div className='markdown-container'>
									<ReactMarkdown
										remarkPlugins={[remarkGfm]}
										children={String(message.content)}
									/>
								</div>
								{message.context.length > 0 && (
									<ChunkItem chunks={message.context} />
								)}
							</div>
						)}
					</div>
				</div>
			)}
		</>
	)
}

export default ChatMessage
