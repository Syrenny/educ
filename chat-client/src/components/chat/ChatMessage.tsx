import type { Message } from '../../types'
import { v4 as uuidv4 } from 'uuid'
import IconLoading from '../icons/IconLoading'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ChatMessageProps {
	loading: boolean
	message: Message
}

const ChatMessage = ({ loading, message }: ChatMessageProps) => {

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
							<div className='disabled w-full appearance-none whitespace-break-spaces text-wrap break-words bg-inherit px-5 py-3.5 text-gray-500 dark:text-gray-400'>
								{message.content ? (
									message.content.trim()
								) : (
									<div>
										<h4 className='mb-1.5 mt-4 pl-0.5 text-sm text-gray-400 first:mt-0 dark:text-gray-500'>
											#{message.action}
										</h4>
										{message.snippet?.trim()}
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
					<div className='relative min-h-[calc(2rem+theme(spacing[3.5])*2)] min-w-[60px] break-words rounded-2xl border border-gray-100 bg-gradient-to-br from-gray-50 px-5 py-3.5 text-gray-600 prose-pre:my-2 dark:border-gray-800 dark:from-gray-800/40 dark:text-gray-300'>
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
							</div>
						)}
					</div>
				</div>
			)}
		</>
	)
}

export default ChatMessage
