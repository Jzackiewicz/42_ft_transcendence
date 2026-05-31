import { useRef } from 'react'
import './AvatarView.css'
import { AVATAR_PRESETS, useAvatarView } from './useAvatarView'

function AvatarView() {
    const { selectedIndex, setSelectedIndex } = useAvatarView()
    const fileRef = useRef<HTMLInputElement>(null)

    return (
        <div className="section-card">
            <div className="section-title">🎭 Avatar</div>

            <div>
                <div className="av-label">Choose Preset</div>
                <div className="av-grid">
                    {AVATAR_PRESETS.map((preset, i) => (
                        <div
                            key={i}
                            className={`av-option ${selectedIndex === i ? 'selected' : ''}`}
                            style={{ background: preset.grad }}
                            onClick={() => setSelectedIndex(i)}
                        >
                            {preset.initials[0]}
                        </div>
                    ))}
                </div>
            </div>

            <div>
                <div className="av-label">Or Upload Photo</div>
                <div className="av-upload-zone" onClick={() => fileRef.current?.click()}>
                    <span className="av-upload-icon">📸</span>
                    <div className="av-upload-text">
                        <strong>Click to upload</strong> or drag & drop
                        <br />
                        <span>PNG, JPG up to 2 MB</span>
                    </div>
                </div>
                <input
                    ref={fileRef}
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                />
            </div>
        </div>
    )
}

export default AvatarView
