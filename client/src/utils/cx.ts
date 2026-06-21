// cx — tiny classNames helper for composing CSS Module classes.
//
// Accepts strings, falsy values (skipped), and { className: condition } maps.
// Designed for the CSS Modules migration where class lists are built
// conditionally, e.g. cx(styles.tab, isActive && styles.active).
//
// Examples:
//   cx(styles.btn, styles.primary)                       -> "btn_x1 primary_y2"
//   cx(styles.tab, isActive && styles.active)            -> "tab_a1 active_b2" | "tab_a1"
//   cx(styles.card, { [styles.error]: hasError })        -> "card_c1 error_d2" | "card_c1"

type ClassValue = string | false | null | undefined | Record<string, boolean>;

export function cx(...values: ClassValue[]): string {
    const out: string[] = [];
    for (const value of values) {
        if (!value) continue;
        if (typeof value === 'string') {
            out.push(value);
        } else {
            for (const key in value) {
                if (value[key]) out.push(key);
            }
        }
    }
    return out.join(' ');
}
