import React, { useEffect, useRef, useState } from 'react'
import { useAction } from '../../context/ActionContext'
import { Action } from '../../types'

export const PDFContextMenu: React.FC = () => {
    const { setAction, setSnippet } = useAction()
	const [visible, setVisible] = useState(false)
	const [coords, setCoords] = useState({ x: 0, y: 0 })
	const [selectedText, setSelectedText] = useState('')
	const menuRef = useRef<HTMLDivElement>(null)

	const hideMenu = () => setVisible(false)

	const handleContextMenu = (event: MouseEvent) => {

		const selection = window.getSelection()
		const text = selection?.toString().trim()

		if (text && text.length > 0) {
			event.preventDefault()
			setSelectedText(text)
			setCoords({ x: event.pageX, y: event.pageY })
			setVisible(true)
		} else {
			hideMenu()
		}
	}

	const handleClick = () => hideMenu()

	const handleAction = (action: Action) => {
		hideMenu()
		if (!selectedText) return

		setSnippet(selectedText)
		setAction(action)
	}

	useEffect(() => {
		document.addEventListener('contextmenu', handleContextMenu)
		document.addEventListener('click', handleClick)
		return () => {
			document.removeEventListener('contextmenu', handleContextMenu)
			document.removeEventListener('click', handleClick)
		}
	}, [selectedText])

	return visible ? (
		<div
			ref={menuRef}
			className='absolute z-[9999] bg-white border border-gray-300 shadow-lg text-sm font-sans rounded w-48'
			style={{ top: coords.y, left: coords.x }}
		>
			<button
				className='block w-full px-4 py-2 text-left hover:bg-gray-100'
				onClick={() => handleAction(Action.Explain)}
			>
				Объяснить
			</button>
			<button
				className='block w-full px-4 py-2 text-left hover:bg-gray-100'
				onClick={() => handleAction(Action.Translate)}
			>
				Перевести на русский
			</button>
		</div>
	) : null
}
