if (!crypto.randomUUID) {
  crypto.randomUUID = () => {
    return ([1e7].toString() + "-1e3-4e3-8e3-1e11").replace(/[018]/g, (c) => {
      const random = crypto.getRandomValues(new Uint8Array(1))[0];
      return (
        parseInt(c, 16) ^
        (random & (15 >> (parseInt(c, 16) / 4)))
      ).toString(16);
    }) as `${string}-${string}-${string}-${string}-${string}`;
  };
}

export const chatUUID = crypto.randomUUID();
