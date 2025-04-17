import React, { useState, useRef, useEffect } from 'react'
import { createStreamChatCompletions, getHistory } from '../api/api'
import type { FileMeta, Message } from '../types'

interface ChatProps {
	file_meta: FileMeta
}

const Chat = ({ file_meta }: ChatProps) => {
	const history = useRef<Message[]>([])
	const [messages, setMessages] = useState<Message[]>([])
	const [input, setInput] = useState<string>('')
	const [isLoading, setIsLoading] = useState(false)

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

	const handleSendMessage = async () => {
		const userMessage: Message = {
			file_meta,
			content: input,
			is_user: true,
		}

        history.current.push(userMessage)
		setMessages([...history.current])
		setInput('')
		setIsLoading(true)

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
								const last =
									history.current[history.current.length - 1]
								if (last && !last.is_user) {
									last.content += delta
								} else {
									history.current.push({
										file_meta,
										content: delta,
										is_user: false,
									})
								}
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

	return (
		<div className='flex flex-col h-full'>
			<div className='flex-grow overflow-auto p-4 space-y-2'>
				{messages.map((msg, index) => (
					<div
						key={index}
						className={`${
							msg.is_user ? 'text-right' : 'text-left'
						}`}
					>
						<div
							className={`inline-block px-3 py-2 rounded-xl ${
								msg.is_user
									? 'bg-blue-500 text-white'
									: 'bg-gray-200 text-black'
							}`}
						>
							{msg.content}
						</div>
					</div>
				))}
			</div>
			<div className='p-4'>
				<input
					value={input}
					onChange={e => setInput(e.target.value)}
					className='w-full p-2 border border-gray-300 rounded'
					placeholder='Введите сообщение...'
				/>
				<button
					onClick={handleSendMessage}
					disabled={isLoading || input.trim() === ''}
					className='w-full mt-2 bg-blue-500 hover:bg-blue-600 text-white font-bold p-2 rounded disabled:opacity-50'
				>
					{isLoading ? 'Отправка...' : 'Отправить'}
				</button>
			</div>
		</div>
	)
}

export default Chat
