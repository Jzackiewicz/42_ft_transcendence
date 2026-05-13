interface InputFieldProps {
    title?: string;
    value: string;
    type: string;
    placeholder?: string;
    onChange: (value: string) => void; // callback function to handle changes in the input field
}

function InputField({ title, value, type, placeholder, onChange }: InputFieldProps) {
    return (
        <div className="field"> 
            <label className="field-label">{title}</label>
            <input  className="field-input"
                    type={type} 
                    value={value}
                    placeholder={placeholder} 
                    onChange={e => onChange(e.target.value)} />
        </div>
    )
}

export default InputField;