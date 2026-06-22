import { useRegistrationView } from './useRegistrationView'
import InputField from '../../../../components/InputField/InputField'
import { Button } from '../../../../components/Button/Button'
import GoogleSignInButton from '../../../../components/GoogleSignInButton/GoogleSignInButton'
import styles from '../../AuthPage.module.css'

interface RegistrationProps {
    onSuccess: () => void
}

function RegistrationView({onSuccess}: RegistrationProps) {
    const { username, setUsername, email, setEmail, password, setPassword, confPassword, setConfPassword, handleRegister, errors } = useRegistrationView(onSuccess)

    return (
        <div className={styles.registrationView}>
            <form onSubmit={(e) => {e.preventDefault(); handleRegister()}}>
                <InputField title= "Display Name" type="text" placeholder="Enter your nickname" value={username} onChange={(value) => setUsername(value)} error={errors.usernameIsEmptyErr} />
                <InputField title="Email" type="email" placeholder="your_email@gmail.com" value={email} onChange={(value) => setEmail(value)} error={errors.mailIsEmptyErr} />
                <InputField title="Password" type="password" placeholder="Create a password" value={password} onChange={(value) => setPassword(value)} error={errors.passIsEmptyErr || errors.passWeakErr} />
                <InputField title="Confirm Password" type="password" placeholder="Confirm your password" value={confPassword} onChange={(value) => setConfPassword(value)} error={errors.confirmPassIsEmptyErr || errors.passDoesntMatchErr} />
                {errors.generalErr && <span className={styles.formError}>{errors.generalErr}</span>}
                <Button type="submit" variant="gradient" size="lg" fullWidth> Register </Button>
                <div className={styles.authDivider}>or</div>
                <GoogleSignInButton label="Sign up with Google" />
            </form>
        </div>
    )
}

export default RegistrationView;