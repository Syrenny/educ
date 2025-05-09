import { useEffect, useRef, useState } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { createStreamChatCompletions, getHistory } from '../../api/api'
import { useAction } from '../../context/ActionContext'
import { Action, FileMeta, Message } from '../../types'
import ChatInput from './ChatInput'
import { ChatIntroduction } from './ChatIntroduction'
import ChatMessage from './ChatMessage'
import { useParams } from 'react-router-dom'

interface ChatProps {
	file_meta: FileMeta
}

const Chat = ({ file_meta }: ChatProps) => {
	const chatContainerRef = useRef<HTMLDivElement | null>(null)
	const history = useRef<Message[]>([])
	const [messages, setMessages] = useState<Message[]>([])
	const [input, setInput] = useState<string>('')
	const [isLoading, setIsLoading] = useState(false)

	const { pdf_action, pdf_snippet } = useAction()

	const scrollToBottom = async () => {
		if (chatContainerRef.current) {
			await new Promise(resolve => setTimeout(resolve, 0))
			chatContainerRef.current.scrollTop =
				chatContainerRef.current.scrollHeight
		}
	}

	useEffect(() => {
		scrollToBottom()
	}, [messages])

	useEffect(() => {
		const loadMessages = async () => {
			try {
				const loadedMessages = await getHistory(file_meta.file_id)
				history.current = loadedMessages
				setMessages([...history.current])
			} catch (error) {
				console.error('Error loading chat messages', error)
			}
		}

		loadMessages()
	}, [file_meta])

	useEffect(() => {
		const targetActions = [Action.Translate, Action.Explain]
		if (targetActions.includes(pdf_action)) {
			handleSendMessage(pdf_action)
		}
	}, [pdf_action])

	const onData = (data: string) => {
		const last = history.current[history.current.length - 1]
		last.content += data
		setMessages([...history.current])
	}

	const onDone = () => {
		setIsLoading(false)
	}

	const onContext = (context: string[]) => {
		const last = history.current[history.current.length - 1]
		last.context = context
		setMessages([...history.current])
	}

	const handleSendMessage = async (act: Action) => {
		if (!isLoading) {
			const userMessage: Message = {
				id: uuidv4(),
				file_meta: file_meta,
				content: input,
				is_user: true,
				action: act,
				snippet: pdf_snippet,
				context: [],
			}

			history.current.push(userMessage)

			const newAssistantMessage: Message = {
				id: uuidv4(),
				file_meta: file_meta,
				content: '',
				is_user: false,
				action: act,
				snippet: pdf_snippet,
				context: [],
			}

			history.current.push(newAssistantMessage)

			setMessages([...history.current])
			setInput('')
			setIsLoading(true)

			await createStreamChatCompletions(
				userMessage,
				onData,
				onContext,
				onDone
			)
		}
	}

	return (
		<div className='relative min-h-0 min-w-0 h-full'>
			<div
				ref={chatContainerRef}
				className='h-full overflow-y-auto [&::-webkit-scrollbar]:w-2
  [&::-webkit-scrollbar-track]:rounded-full
  [&::-webkit-scrollbar-track]:bg-transparent
  [&::-webkit-scrollbar-thumb]:rounded-full
  [&::-webkit-scrollbar-thumb]:bg-gray-500
  dark:[&::-webkit-scrollbar-track]:bg-transparent
  dark:[&::-webkit-scrollbar-thumb]:bg-neutral-500'
			>
				<div className='mx-auto flex h-full max-w-3xl flex-col gap-6 px-5 pt-6 sm:gap-8 xl:max-w-4xl xl:pt-10'>
					<div className='flex h-max flex-col gap-8 pb-52'>
						{messages.length > 0 ? (
							messages.map((msg, index) => (
								<ChatMessage
									key={msg.id}
									message={msg}
									loading={isLoading}
								/>
							))
						) : (
							<ChatIntroduction />
						)}
					</div>
				</div>
			</div>
			<div className='dark:via-gray-80 pointer-events-none absolute inset-x-0 bottom-0 z-0 mx-auto flex w-full max-w-3xl flex-col items-center justify-center bg-gradient-to-t from-white via-white/80 to-white/0 px-3.5 py-4 dark:border-gray-800 dark:from-gray-900 dark:to-gray-900/0 max-md:border-t max-md:bg-white max-md:dark:bg-gray-900 sm:px-5 md:py-8 xl:max-w-4xl [&>*]:pointer-events-auto'>
				<ChatInput
					disabled={isLoading}
					onChange={setInput}
					onSubmit={() => {
						handleSendMessage(Action.Default)
					}}
				/>
			</div>
		</div>
	)
}

export default Chat
