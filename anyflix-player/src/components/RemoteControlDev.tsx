import { useKeyRemoteNavigationContext } from "@/hooks/KeyRemoteNavigationProvider";

export function RemoteControlDev() {
  const { coordinates, okSelect, keyEvent } = useKeyRemoteNavigationContext();

  return (
    <div className="container mt-16 mx-auto p-4 text-black">
      <div className="annotation flex  gap-2 bg-gray-100 p-2 rounded shadow-md">
        <button tabIndex={0} className="coordinates  border-b pb-2">
          <header className="font-bold text-lg mb-2">Coordinates</header>
          <p className="text-sm">
            X: <span className="x_coor font-mono">{coordinates.x}</span>
          </p>
          <p className="text-sm">
            Y: <span className="y_coor font-mono">{coordinates.y}</span>
          </p>
        </button>
        <button tabIndex={0} className="okstatus border-b pb-2">
          <header className="font-bold text-lg mb-2">OK Click</header>
          <p className="ok_select text-sm">{okSelect}</p>
        </button>
        <button tabIndex={0} className="input_key_event">
          <header className="font-bold text-lg mb-2">Input Key Event</header>
          <p className="text-sm">
            Key Name: <span className="key_name font-mono">{keyEvent.key}</span>
          </p>
          <p className="text-sm">
            Key Code:{" "}
            <span className="key_code font-mono">{keyEvent.keyCode}</span>
          </p>
          <p className="text-sm">
            Key Status:{" "}
            <span className="key_status font-mono">{keyEvent.keyStatus}</span>
          </p>
        </button>
      </div>

      <div className="main_container mt-6">
        <div className="header flex justify-around bg-blue-200 p-2 rounded mb-4">
          <button
            className="item cursor-pointer hover:bg-blue-300 p-2 rounded"
            tabIndex={0}
            id="header1"
          >
            header 1
          </button>
          <button
            className="item cursor-pointer hover:bg-blue-300 p-2 rounded"
            tabIndex={0}
            id="header2"
          >
            header 2
          </button>
        </div>
        <div className="row flex flex-col md:flex-row gap-4">
          <div className="side flex flex-col gap-2 bg-green-100 p-2 rounded">
            <button
              className="item cursor-pointer hover:bg-green-200 p-2 rounded"
              tabIndex={0}
              id="side1"
            >
              side 1
            </button>
            <button
              className="item cursor-pointer hover:bg-green-200 p-2 rounded"
              tabIndex={0}
              id="side2"
            >
              side 2
            </button>
            <button
              className="item cursor-pointer hover:bg-green-200 p-2 rounded"
              tabIndex={0}
              id="side3"
            >
              side 3
            </button>
            <button
              className="item cursor-pointer hover:bg-green-200 p-2 rounded"
              tabIndex={0}
              id="side4"
            >
              side 4
            </button>
          </div>
          <div className="main grid grid-cols-3 gap-2 bg-yellow-100 p-2 rounded">
            {Array.from({ length: 15 }, (_, index) => {
              const id = `item${index + 1}`;
              return (
                <button
                  key={id}
                  className="item cursor-pointer hover:bg-yellow-200 p-2 rounded"
                  tabIndex={0}
                  id={id}
                >
                  {id}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
