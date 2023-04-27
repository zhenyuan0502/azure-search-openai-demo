import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    {
        text: "Bạn có thể cung cấp thông tin thẻ tín dụng ngân hàng nào?",
        value: "Bạn có thể cung cấp thông tin thẻ tín dụng ngân hàng nào?"
    },
    { text: "Techcombank có các loại thẻ tín dụng nào?", value: "Techcombank có các loại thẻ tín dụng nào?" },
    { text: "Ngân hàng nào đang có lãi suất cao nhất?", value: "Ngân hàng nào đang có lãi suất cao nhất?" }
];

interface Props {
    onExampleClicked: (value: string) => void;
}

export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <li key={i}>
                    <Example text={x.text} value={x.value} onClick={onExampleClicked} />
                </li>
            ))}
        </ul>
    );
};
