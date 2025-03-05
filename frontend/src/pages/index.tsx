import { Box, Button, Center, Group, Pagination, TextInput, Text, Title, Checkbox } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState } from "react";
import Enumerable from "linq";
import { PageToShow } from "@/components/Page";
import { notifications } from "@mantine/notifications";
import { env } from "@/env";

type DataType = {
  documentId: number;
  weight: number;
}[];

const perPage = 5;

export default function Home() {
  const [data, setData] = useState<DataType>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [tookTime, setTookTime] = useState<number | null>(null);
  const [showWeights, setShowWeights] = useState(false);
  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      expression: '',
    },
  });
  const getData = (expression: string) => {
    if (expression === "") {
      setData([]);
      setTookTime(null);
      return;
    }
    (async () => {
      try {
        const start = performance.now();
        setLoading(true);
        const res = await fetch(`${env.NEXT_PUBLIC_BACKEND_URL}/query?query=${expression}`);
        if (res.status === 400) {
          notifications.show({
            title: 'Error',
            message: await res.text(),
            color: "red",
          });
          setData([]);
        } else {
          const data = await res.json() as DataType;
          setData(data.sort((a, b) => b.weight - a.weight));
        }
        const end = performance.now();
        setTookTime(end - start);
      } catch (e) {
        setData([]);
        setTookTime(null);
        notifications.show({
          title: 'Error',
          message: "Unknown error",
          color: "red",
        });
      }
      finally {
        setLoading(false);
        setPage(1);
      }

    })();
  }
  const optimization = async (enable: boolean) => {
    try {
      setLoading(true);
      await fetch(`${env.NEXT_PUBLIC_BACKEND_URL}/optimization-${enable ? "on" : "off"}`, {
        method: "POST",
      });
      notifications.show({
        title: "Success",
        message: "Optimization successfully updated"
      });
    } catch (e) {
      notifications.show({
        title: 'Error',
        message: "Unknown error",
        color: "red",
      });
    } finally {
      setLoading(false);
    }
  }
  const dataToShow = Enumerable.from(data).skip((page - 1) * perPage).take(perPage).toArray();
  return (
    <Box maw={840} mx="auto">
      <Center>
        <Title>Harry Potter 1-4 Search</Title>
      </Center>
      <Box maw={340} mx="auto">
        <form onSubmit={form.onSubmit((values) => getData(values.expression))}>
          <TextInput
            withAsterisk
            label="Your expression"
            placeholder="Harry and Hermiona"
            key={form.key('expression')}
            spellCheck={false}
            {...form.getInputProps('expression')}
          />
          <Group justify="flex-end" mt="md">
            <Button type="submit" disabled={loading}>Submit</Button>
          </Group>
        </form>
      </Box>
      <Text>Results: {data.length}</Text>
      {tookTime && (
        <Text>It took: {tookTime}ms</Text>
      )}
      {dataToShow.map((data, i) => (
        <PageToShow key={data.documentId} documentId={data.documentId} pageNumber={(page - 1) * perPage + i + 1} weight={data.weight} showWeight={showWeights} />
      ))}
      <Center my={10}>
        <Pagination total={Math.ceil(data.length / perPage)} onChange={setPage} value={page} />
      </Center>
      <Center>
        <Box>
          <Button m={2} onClick={() => optimization(true)} disabled={loading}>Add optimization</Button>
          <Button m={2} onClick={() => optimization(false)} disabled={loading}>Remove optmization</Button>
        </Box>
      </Center>
      <Center>
        <Box>
        <Checkbox
          checked={showWeights}
          onClick={() => setShowWeights((x) => !x)}
          label="Show weights"
          m={5}
        />
        </Box>
      </Center>
    </Box>
  );
}
