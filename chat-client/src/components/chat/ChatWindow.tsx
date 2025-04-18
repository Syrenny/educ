import { useEffect, useRef, useState } from 'react'
import { createStreamChatCompletions, getHistory } from '../../api/api'
import ChatInput from './ChatInput'
import ChatMessage from './ChatMessage'
import { FileMeta, Message, ShortcutAction } from '../../types'
import { useShortcut } from '../../context/ShortcutContext'

interface ChatProps {
	file_meta: FileMeta
}

const Chat = ({ file_meta }: ChatProps) => {
	const chatContainerRef = useRef<HTMLDivElement | null>(null)
	const history = useRef<Message[]>([])
	const [messages, setMessages] = useState<Message[]>([])
	const [input, setInput] = useState<string>('')
	const [isLoading, setIsLoading] = useState(false)
    const { shortcut } = useShortcut()

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
        if (shortcut) {
		    if (shortcut.action === ShortcutAction.Translate || shortcut.action === ShortcutAction.Explain) {
                handleShortcutMessage()
            }

        }
	}, [shortcut])


    const sendToServer = async (userMessage: Message) => {
        try {
            const reader = await createStreamChatCompletions(userMessage)
            const decoder = new TextDecoder('utf-8')

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value, { stream: true })

                chunk.split('\n').forEach(line => {
                    if (line.startsWith('data: ')) {
                        const data = line.replace('data: ', '').trim()

                        if (data === '[DONE]') return

                        try {
                            const json = JSON.parse(data)
                            const delta = json.choices?.[0]?.delta?.content
                            if (delta) {
                                const last = history.current[history.current.length - 1]
                                last.content += delta
                                setMessages([...history.current])
                            }
                        } catch (err) {
                            console.warn('JSON parse error in stream', err)
                        }
                    }
                })
            }
        } catch (error) {
            console.error('Error fetching chat completion', error)
        } finally {
            setIsLoading(false)
        }
    }

	const handleSendMessage = async () => {
		const userMessage: Message = {
			file_meta,
			content: input,
			is_user: true,
            shortcut: null
		}

		history.current.push(userMessage)
        
        const newAssistantMessage: Message = {
			file_meta,
			content: "",
			is_user: false,
            shortcut: null
		}

        history.current.push(newAssistantMessage)

		setMessages([...history.current])
		setInput('')
		setIsLoading(true)

		sendToServer(userMessage)
	}

    const handleShortcutMessage = async () => {
        if (shortcut) {
            const shortcutMessage: Message = {
                file_meta,
                content: "",
                is_user: true,
                shortcut: shortcut
            }

            history.current.push(shortcutMessage)

            const newAssistantMessage: Message = {
                file_meta,
                content: '',
                is_user: false,
                shortcut: null
            }

            history.current.push(newAssistantMessage)

            setMessages([...history.current])
            setInput('')
            setIsLoading(true)

            sendToServer(shortcutMessage)
        }
	}

	return (
		<div className='relative min-h-0 min-w-0 h-full'>
			<div ref={chatContainerRef} className='scrollbar-custom h-full overflow-y-auto'>
				<div className='mx-auto flex h-full max-w-3xl flex-col gap-6 px-5 pt-6 sm:gap-8 xl:max-w-4xl xl:pt-10'>
					<div className='flex h-max flex-col gap-8 pb-52'>
						{messages.map((msg, index) => (
							<ChatMessage message={msg} loading={isLoading} />
						))}
					</div>
				</div>
			</div>
			<div className='dark:via-gray-80 pointer-events-none absolute inset-x-0 bottom-0 z-0 mx-auto flex w-full max-w-3xl flex-col items-center justify-center bg-gradient-to-t from-white via-white/80 to-white/0 px-3.5 py-4 dark:border-gray-800 dark:from-gray-900 dark:to-gray-900/0 max-md:border-t max-md:bg-white max-md:dark:bg-gray-900 sm:px-5 md:py-8 xl:max-w-4xl [&>*]:pointer-events-auto'>
				<ChatInput
					disabled={isLoading}
					onChange={setInput}
					onSubmit={handleSendMessage}
				/>
			</div>
		</div>
	)
}

export default Chat
