import styles from './InputField.module.css';

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
        <div className={styles.field}>
            <label className={styles['field-label']}>{title}</label>
            <input  className={styles['field-input']}
                    type={type}
                    value={value}
                    placeholder={placeholder}
                    onChange={e => onChange(e.target.value)} />
            {error && <span className={styles['inputfield-warning']}>{error}</span>}
        </div>
    )
}

export default InputField;