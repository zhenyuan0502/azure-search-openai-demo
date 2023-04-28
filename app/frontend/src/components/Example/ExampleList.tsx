import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    {
        text: "Thông số xe Vinfast 8",
        value: "Thông số xe Vinfast 8"
    },
    { text: "Giá lăn bánh Vinfast 8 là bao nhiêu?", value: "Giá lăn bánh Vinfast 8 là bao nhiêu?" },
    { text: "VF8 có bao nhiêu màu?", value: "VF8 có bao nhiêu màu?" }
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
