import { env } from "@/env";
import { Loader, Text, Title } from "@mantine/core";
import React, { FC, useEffect, useState } from "react";

type PageToShowProps = {
	pageNumber: number;
	documentId: number;
	weight: number;
	showWeight: boolean;
};

export const PageToShow: FC<PageToShowProps> = ({ documentId, pageNumber, weight, showWeight }) => {
	const [data, setData] = useState<string | null>(null);
	useEffect(() => {
		(async () => {
			try {
				const res = await fetch(`${env.NEXT_PUBLIC_BACKEND_URL}/get?documentId=${documentId}`);
				const text = await res.text();
				setData(text);
			} catch (e) { }
		})();
	}, [documentId]);
	if (!data)
		return (
			<Loader />
		);
	return (
		<div>
			<Title>{pageNumber}</Title>
			{showWeight && <Text>Weight: {weight}</Text>}
			<Text>{data}</Text>
		</div>
	);
};

