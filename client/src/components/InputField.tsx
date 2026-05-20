interface InputFieldProps {
    title?: string;
    value: string;
    type: string;
    placeholder?: string;
    error?: string
    onChange: (value: string) => void; // callback function to handle changes in the input field
}

function InputField({ title, value, type, placeholder, error, onChange }: InputFieldProps) {
    return (
        <div className="field"> 
            <label className="field-label">{title}</label>
            <input  className="field-input"
                    type={type}
                    value={value}
                    placeholder={placeholder}
                    onChange={e => onChange(e.target.value)} />
            {error && <span>{error}</span>}
        </div>
    )
}

export default InputField;